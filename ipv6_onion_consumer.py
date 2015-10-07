from scapy.all import IPv6
from zope.interface import implementer
import struct

from twisted.internet import interfaces
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.internet import defer
from twisted.python import log
from twisted.internet.protocol import Factory, Protocol

from convert import convert_ipv6_to_onion



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
        self.producer = None
        self.onion_conn_d = defer.succeed(None)
        self.pool = {}

    def logPrefix(self):
        return 'IPv6OnionConsumer'

    def write_to_onion(self, protocol, packet):
        print('writing packet to onion')
        packet_len = len(packet)
        data = struct.pack('!H', packet_len) + packet
        print "PROTOCOL %s" % (protocol,)
        print "TRANSPORT %s" % (protocol.transport,)
        protocol.transport.write(data)
        return None

    def onionConnectionFailed(self, failure):
        log.msg('onion connection failed')
        print(type(failure.value), failure)

    def getOnionConnection(self, onion):
        """ getOnionConnection returns a deferred which fires
        with a client connection to an onion address.
        """
        if onion in self.pool:
            log.msg("Found onion connection in pool to %s.onion" % onion)
            return defer.succeed(self.pool[onion])
        else:
            log.msg("Did not find connection to %s.onion in pool" % onion)
            tor_endpoint = clientFromString(
                self.reactor, "tor:%s.onion:80" % onion)

            print(tor_endpoint)
            p = Protocol()
            p.onion = onion

            d = connectProtocol(tor_endpoint, p)
            def add_to_pool(result):
                self.pool[onion] = result
            d.addCallback(add_to_pool)
            return d

    # IConsumer section
    def write(self, packet):
        """
        Tries to determine the destination onion address, create a client
        connection to that endpoint, and send the data.
        """

        log.msg("IPv6OnionConsumer.write() called")
        try:
            ip_packet = IPv6(packet)
            # XXX assert that the source address is correct?
        except struct.error:
            log.msg("not an IPv6 packet")
            return
        onion = convert_ipv6_to_onion(ip_packet.dst)
        print("Onion connection: {} -> {}".format(ip_packet.dst, onion))

        self.onion_conn_d.addCallback(lambda ign: self.getOnionConnection(onion))
        # Send data when connection opens
        self.onion_conn_d.addCallback(lambda protocol: self.write_to_onion(protocol, packet))
        self.onion_conn_d.addErrback(self.onionConnectionFailed)

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
