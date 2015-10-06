from scapy.all import IPv6
from zope.interface import implementer
import socket
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
        print "------- addr onion uri == %s" % (addr.onion_uri,)
        # XXX correct?
        p = self.protocol()
        self.pool[addr.onion_uri] = p
        p.factory = self
        return p

@implementer(interfaces.IConsumer)
class IPv6OnionConsumer(object):

    def __init__(self, reactor):
        super(IPv6OnionConsumer, self).__init__()
        print "IPv6OnionConsumer init"
        self.reactor = reactor
        self.pooledOnionFactory = PooledOnionFactory()
        self.producer = None

    def logPrefix(self):
        return 'IPv6OnionConsumer'

    def getOnionConnection(self, onion):
        """ getOnionConnection returns a deferred which fires
        with a client connection to an onion address.
        """
        if onion in self.pooledOnionFactory.pool:
            return defer.succeed(self.pooledOnionFactory.pool[onion])
        else:
            torEndpoint = clientFromString(self.reactor, "tor:%s.onion:666" % onion)
            d = torEndpoint.connect(self.pooledOnionFactory)
            return d

    # IConsumer section
    def write(self, packet):
        print "write()"
        try:
            ip_packet = IPv6(packet)
            # XXX assert that the source address is correct?
        except struct.error:
            log.msg("not an IPv6 packet")
            return
        print "ipv6 onion consumer: write: ip dest: %s" % (ip_packet.dst,)
        onion = convert_ipv6_to_onion(ip_packet.dst)
        d = self.getOnionConnection(onion)
        d.addCallback(lambda p: p.transport.write(packet))
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
