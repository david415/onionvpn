from scapy.all import IPv6
from zope.interface import implementer
import struct

from twisted.internet import interfaces
from twisted.internet.endpoints import clientFromString
from twisted.internet import defer
from twisted.python import log
from twisted.internet.protocol import Factory

from convert import convert_ipv6_to_onion


class PooledOnionFactory(Factory):
    def __init__(self):
        print "PooledOnionFactory init"
        self.pool = set()

    def buildProtocol(self, addr):
        print "PooledOnionFactory buildProtocol addr %s" % (addr,)
        # XXX todo: assert type TorOnionAddress
        print(dir(addr))
        # print "------- addr onion uri == %s" % (addr.onion_uri,)
        # XXX correct?
        p = self.Protocol()
        self.pool[addr.onion_uri] = p
        p.factory = self
        return p


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
        self.pooledOnionFactory = PooledOnionFactory()
        self.producer = None

    def logPrefix(self):
        return 'IPv6OnionConsumer'

    def write_to_onion(self, tor_endpoint, packet):
        print('writing packet to onion')
        tor_endpoint.transport.write(packet)

    def onionConnectionFailed(self, failure):
        log.msg('onion connection failed')
        print(type(failure.value), failure)

    def getOnionConnection(self, onion):
        """ getOnionConnection returns a deferred which fires
        with a client connection to an onion address.
        """
        if onion in self.pooledOnionFactory.pool:
            log.msg("Found onion connection in pool to %s.onion" % onion)
            return defer.succeed(self.pooledOnionFactory.pool[onion])
        else:
            log.msg("Did not find connection to %s.onion in pool" % onion)
            tor_endpoint = clientFromString(
                self.reactor, "tor:%s.onion:80" % onion)

            print(tor_endpoint)
            d = tor_endpoint.connect(self.pooledOnionFactory)
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

        d = self.getOnionConnection(onion)
        # Send data when connection opens
        d.addCallback(self.write_to_onion, packet)
        d.addErrback(self.onionConnectionFailed)
        # XXX dropped deferred

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
