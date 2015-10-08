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
    def __init__(self, maxlen, clock, handle_packet):
        self.maxlen = maxlen
        self.clock = clock
        self.handle_packet = handle_packet

        self.turn_delay = 0
        self.deque = deque(maxlen=self.maxlen)
        self.is_ready = False
        self.stopped = False
        self.lazy_tail = defer.succeed(None)

    def ready(self):
        self.is_ready = True
        self.turn_deque()

    def stop(self):
        self.stopped = True
        self.is_ready = False

    def append(self, packet):
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

    def onionConnectionFailed(self, failure):
        log.msg('onion connection failed')
        print(type(failure.value), failure)

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
            d = connectProtocol(tor_endpoint, protocol)
            def onionReconnect():
                d = connectProtocol(tor_endpoint, protocol)
                d.addErrback(handleConnectFail)
                return d
            def handleConnectFail(failure):
                return onionReconnect()
            d.addErrback(handleConnectFail)
            return d

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

        if onion not in self.onion_packet_queue_map:
            self.onion_packet_queue_map[onion] = PacketDeque(self.deque_max_len, self.reactor, lambda packet: self.write_to_onion(onion, packet))
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
