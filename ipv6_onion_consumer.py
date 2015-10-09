from scapy.all import IPv6
from zope.interface import implementer
import struct
from collections import deque
from txsocksx import errors

from twisted.internet import interfaces, task, error
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
        print "CREATE NEW PACKET DEQUE"
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
        print "ready"
        self.is_ready = True
        self.stopped = False
        self.turn_deque()

    def pause(self):
        print "pause"
        self.is_ready = False
        self.stopped = True

    def call_forget_peer(self):
        print "call_forget_peer"
        if len(self.deque) == 0:
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
            self.forget_peer_timer.reset(self.forget_duration)

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

    def turn_deque(self):
        print "turn_deque"
        if self.stopped:
            print "turn_deque stopped"
            return
        try:
            packet = self.deque.pop()
        except IndexError:
            self.lazy_tail.addCallback(lambda ign: defer.succeed(None))
            print "index error stopping lazytail"
        else:
            self.lazy_tail.addCallback(lambda ign: self.handle_packet(packet))
            self.lazy_tail.addErrback(log.err)
            self.lazy_tail.addCallback(lambda ign: task.deferLater(self.clock, self.turn_delay, self.turn_deque))
            print "pushed handling of packet onto lazytail"


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
        self.deque_max_len = 40
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

    def try_onion_connect(self, onion):
        print "try_onion_connection %s" % (onion,)
        protocol = Protocol()
        protocol.onion = onion
        def handleLostConnection(failure):
            print "handleLostConnection %s" % (failure,)
            failure.trap(error.ConnectionClosed)
            print "after handleLostConnection trap"
            self.forget_peer(onion)
        protocol.connectionLost = handleLostConnection
        tor_endpoint = clientFromString(
            self.reactor, "tor:%s.onion:80" % onion)
        d = connectProtocol(tor_endpoint, protocol)
        d.addErrback(lambda failure: self.retry_onion_connect(failure, onion))
        return d

    def retry_onion_connect(self, failure, onion):
        print "retry_onion_connect onion %s failure %s" % (onion, failure)
        if not isinstance(failure, errors.SOCKSError) or not isinstance(error.ConnectError):
            return failure

        print "after retry_onion_connect trap"
        # XXX todo: conditional failure to prevent retry goes here
        d = self.try_onion_connect(onion)
        d.addErrback(lambda new_failure: self.retry_onion_connect(new_failure, onion))
        return d

    def forget_peer(self, onion):
        print "--- <> <<>> tearDownOnionDeque with onion %s" % (onion,)
        protocol = None
        if onion in self.onion_packet_queue_map:
            del self.onion_packet_queue_map[onion]
        if onion in self.onion_connected_map:
            self.onion_connected_map[onion].cancel()
            del self.onion_connected_map[onion]
        if onion in self.onion_protocol_map:
            protocol = self.onion_protocol_map[onion]
            del self.onion_protocol_map[onion]
        if protocol is not None:
            protocol.transport.loseConnection()

    # IConsumer section
    def write(self, packet):
        log.msg("self %s IPv6OnionConsumer.write() called" % (self,))
        try:
            ip_packet = IPv6(packet)
        except struct.error:
            log.msg("not an IPv6 packet")
            return
        onion = convert_ipv6_to_onion(ip_packet.dst)
        print("write to onion: {} -> {}".format(ip_packet.dst, onion))
        if onion not in self.onion_packet_queue_map:
            print "onion not found in self.onion_packet_queue_map"
            self.onion_packet_queue_map[onion] = PacketDeque(self.deque_max_len, self.reactor, lambda new_packet: self.write_to_onion(onion, new_packet), lambda: self.forget_peer(onion))
            self.onion_connected_map[onion] = self.try_onion_connect(onion)
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
