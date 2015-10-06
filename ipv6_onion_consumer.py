from scapy.all import IP
from zope.interface import implementer
import socket
#from txtorcon.endpoints import TorOnionAddress

from twisted.internet import interfaces
from twisted.internet import defer
from twisted.python import log
from twisted.internet.protocol import Factory

def convert_ipv6_to_onion(ipv6_addr):
    packet = socket.inet_pton(socket.AF_INET6, ipv6_addr)
    return packet[:10]

class PooledOnionFactory(Factory):
    def __init__(self):
        self.pool = set()

    def buildProtocol(self, addr):
        print "PooledOnionFactory buildProtocol"
        # XXX todo: assert type TorOnionAddress
        print "------- addr onion uri == %s" % (addr.onion_uri,)
        # XXX correct?
        p = self.protocol()
        self.pool[addr.onion_uri] = p
        p.factory = self
        return p

@implementer(interfaces.IConsumer)
class IPv6OnionConsumer(object):

    def __init__(self):
        super(IPv6OnionConsumer, self).__init__()
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
            torEndpoint = clientFromString("tor:%s.onion" % onion)
            d = torEndpoint.connect(self.pooledOnionFactory)
            return d

    # IConsumer section
    def write(self, packet):
        print "write"
        try:
            ip_packet = IP(datagram)
            assert ip_packet.version == 6
            # XXX assert that the source address is correct?
        except struct.error:
            log.msg("not an ip packet")
            return

        onion = convert_ipv6_to_onion(ip_packet.dst)
        d = self.getOnionConnection(onion)
        d.addCallback(lambda p: p.transport.write(packet))
        # XXX dropped deferred

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        assert self.producer is not None
        self.producer.stopProducing()
