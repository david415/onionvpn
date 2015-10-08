from scapy.all import IPv6
from zope.interface import implementer
import struct
from collections import deque

from twisted.internet import interfaces, task
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.internet import defer
from twisted.python import log
from twisted.internet.protocol import Factory, Protocol

from convert import convert_ipv6_to_onion


class PacketDeque(object):
    """
    PacketDeque handles packet queuing for a packet transport system.
    """
    def __init__(self, maxlen, clock, handle_packet, forget_peer):
        self.maxlen = maxlen
        self.clock = clock
        self.handle_packet = handle_packet
        self.forget_peer = forget_peer

        self.turn_delay = 0
        self.deque = deque(maxlen=self.maxlen)
        self.is_ready = False
        self.stopped = False
        self.lazy_tail = defer.succeed(None)
        self.forget_peer_timer = None
        self.clear_deque_timer = None
        # XXX
        self.forget_duration = 300
        self.clear_deque_duration = 10

    def ready(self):
        self.is_ready = True
        self.stopped = False
        self.turn_deque()

    def pause(self):
        self.is_ready = False
        self.stopped = True

    def stop(self):
        self.stop_all_timers()
        self.pause()
        self.deque.clear()

    def call_forget_peer(self):
        if len(self.deque) == 0:
            self.transport.loseConnection()
            self.stop_all_timers()
            self.pause()
            self.deque.clear()
            self.forget_peer()

    def stop_all_timers(self):
        if self.forget_peer_timer.active():
            self.forget_peer_timer.cancel()
        if self.clear_deque_timer.active():
            self.clear_deque_timer.cancel()

    def append(self, packet):
        if self.forget_peer_timer is None:
            self.forget_peer_timer = self.clock.callLater(self.forget_duration, self.call_forget_peer)
        else:
            assert self.forget_peer_timer.active()

        if self.clear_deque_timer is None:
            self.clear_deque_timer = self.clock.callLater(self.clear_deque_duration, self.deque.clear)
        else:
            if self.clear_deque_timer.active():
                self.clear_deque_timer.reset(self.clear_deque_duration)
            else:
                self.clear_deque_timer = self.clock.callLater(self.clear_deque_duration, self.deque.clear)

        self.deque.append(packet)
        if self.is_ready:
            self.clock.callLater(0, self.turn_deque)

    def when_queue_is_empty(self):
        return defer.succeed(None)

    def turn_deque(self):
        if self.stopped:
            return
        try:
            packet = self.deque.pop()
        except IndexError:
            self.lazy_tail.addCallback(lambda ign: self.when_queue_is_empty())
        else:
            self.lazy_tail.addCallback(lambda ign: self.handle_packet(packet))
            self.lazy_tail.addErrback(log.err)
            self.lazy_tail.addCallback(lambda ign: task.deferLater(self.clock, self.turn_delay, self.turn_deque))


@implementer(interfaces.IConsumer)
class IPv6OnionConsumer(object):
    """
    IPv6OnionConsumer accepts IPv6 data written to it by it's write()
    method. The IPv6 packet is parsed to determine the destination IPv6
    address.

    The IPv6 address is converted to an onion address and it attempts
    to open a client connection the the hidden service. A connection is
    selected from the pool if it already exists
    """

    def __init__(self, reactor):
        super(IPv6OnionConsumer, self).__init__()
        print "IPv6OnionConsumer init"
        self.reactor = reactor
        self.deque_max_len = 100
        self.producer = None
        self.pool = {} # XXX
        self.onion_packet_queue_map = {}
        self.onion_connected_map = {}
        self.onion_protocol_map = {}

    def logPrefix(self):
        return 'IPv6OnionConsumer'

    def write_to_onion(self, onion, packet):
        protocol = self.onion_protocol_map[onion]
        packet_len = len(packet)
        framed_packet = struct.pack('!H', packet_len) + packet
        protocol.transport.write(framed_packet)

    def getOnionConnection(self, onion):
        """ getOnionConnection returns a deferred which fires
        with a client connection to an onion address.
        """
        if onion in self.onion_connected_map:
            log.msg("Found onion connection in pool to %s.onion" % onion)
            return defer.succeed(self.onion_connected_map[onion])
        else:
            log.msg("Did not find connection to %s.onion in pool" % onion)
            tor_endpoint = clientFromString(
                self.reactor, "tor:%s.onion:80" % onion)

            print(tor_endpoint)
            protocol = Protocol()
            protocol.onion = onion
            def handleLostConnection(reason):
                self.tearDownOnionDeque(onion)
            protocol.connectionLost = handleLostConnection
            d = connectProtocol(tor_endpoint, protocol)
            def onionReconnect():
                if onion in self.onion_packet_queue_map:
                    d = connectProtocol(tor_endpoint, protocol)
                else:
                    return defer.succeed(None)
                return d
            d.addErrback(lambda reason: onionReconnect())
            return d

    def tearDownOnionDeque(self, onion):
        print "--- <> <<>> tearDownOnionDeque"
        if onion in self.onion_packet_queue_map:
            self.onion_packet_queue_map[onion].stop()
        del self.onion_packet_queue_map[onion]
        del self.onion_connected_map[onion]
        del self.onion_protocol_map[onion]

    # IConsumer section
    def write(self, packet):
        log.msg("IPv6OnionConsumer.write() called")
        try:
            ip_packet = IPv6(packet)
        except struct.error:
            log.msg("not an IPv6 packet")
            return
        onion = convert_ipv6_to_onion(ip_packet.dst)
        print("Onion connection: {} -> {}".format(ip_packet.dst, onion))

        def reject_peer(onion):
            self.tearDownOnionDeque(onion)

        if onion not in self.onion_packet_queue_map:
            self.onion_packet_queue_map[onion] = PacketDeque(self.deque_max_len, self.reactor, lambda packet: self.write_to_onion(onion, packet), lambda: reject_peer(onion))
            self.onion_connected_map[onion] = self.getOnionConnection(onion)

            def connection_ready(onion, protocol):
                self.onion_protocol_map[onion] = protocol
                self.onion_packet_queue_map[onion].ready()

            self.onion_connected_map[onion].addCallback(lambda protocol: connection_ready(onion, protocol))
        self.onion_packet_queue_map[onion].append(packet)

    def registerProducer(self, producer, streaming):
        print "registerProducer"
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        print "unregisterProducer"
        assert self.producer is not None
        self.producer.stopProducing()
