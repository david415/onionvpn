# import stuct
import struct

from zope.interface import implementer
from twisted.internet import interfaces
from twisted.protocols.basic import Int16StringReceiver
from twisted.internet.protocol import Protocol, Factory
from twisted.python import log
from scapy.all import IPv6
from struct import unpack


class PersistentSingletonFactory(Factory):
    def __init__(self, protocol):
        print "PersistentSingletonFactory __init__"
        self.protocol = protocol

    def buildProtocol(self, addr):
        print "PersistentSingletonFactory buildProtocol addr %s" % (addr,)
        return PersistentProtocol(self.protocol)


class PersistentProtocol(Protocol):
    def __init__(self, target_protocol):
        self.target_protocol = target_protocol

    def logPrefix(self):
        return 'PersistentProtocol'

    def dataReceived(self, data):
        print "PersistentProtocol dataReceived"
        self.target_protocol.dataReceived(data)

    def connectionLost(self, reason):
        print "connectionLost %r" % (reason,)

@implementer(interfaces.IPushProducer)
class TcpFrameProducer(Protocol, object):
    def __init__(self, local_addr, consumer=None):
        super(TcpFrameProducer, self).__init__()
        print "TcpFrameProducer init"
        self.local_addr = local_addr
        self.consumer = consumer

    def dataReceived(self, data):
        print "TcpFrameProducer dataReceived"
        self.filter_send(data)

    def filter_send(self, packet):
        try:
            ipv6_packet = IPv6(packet)
        except struct.error:
            print "not an IPv6 packet"
            return # not-send non-ipv6 packets

        # assert that the destination IPv6 address matches our address
        if ipv6_packet.dst != self.local_addr:
            log.msg("dropping packet because ipv6 destination doesn't match our vpn destination")
            return
        # write the IPv6 packet to our consumer
        self.consumer.write(packet)

    def logPrefix(self):
        return 'TcpFrameProducer'

    # IPushProducer
    def pauseProducing(self):
        print "pauseProducing"

    def resumeProducing(self):
        print "resumeProducing"

    def stopProducing(self):
        print "stopProducing"
