# import stuct
import struct

from zope.interface import implementer

from twisted.internet import interfaces
from twisted.protocols.basic import Int16StringReceiver
from twisted.internet.protocol import Protocol, Factory
from twisted.python import log
from scapy.all import IPv6, hexdump


class PersistentSingletonFactory(Factory):
    def __init__(self, protocol):
        print "PersistentSingletonFactory __init__"
        self.protocol = protocol

    def buildProtocol(self, addr):
        print "PersistentSingletonFactory buildProtocol addr %s" % (addr,)
        p = PersistentProtocol(self.protocol)
        return p


class PersistentProtocol(Protocol):
    def __init__(self, target_protocol):
        self.target_protocol = target_protocol

    def logPrefix(self):
        return 'PersistentProtocol'

    def dataReceived(self, data):
        print "PersistentProtocol dataReceived"
        print(self.target_protocol)

        # Forward data from hidden service to TcpFrameProducer.dataReceived()
        # to deframe the data
        self.target_protocol.dataReceived(data)


@implementer(interfaces.IPushProducer)
class TcpFrameProducer(Int16StringReceiver, object):
    def __init__(self, local_addr, consumer=None):
        super(TcpFrameProducer, self).__init__()
        print "TcpFrameProducer init"
        self.local_addr = local_addr
        self.consumer = consumer

    def stringReceived(self, data):
        """
        Called with the packet from the onion interface after it is deframed
        """
        # XXX: This isn't being called when the data isn't framed
        print "stringReceived"
        # assert that it's an IPv6 packet
        try:
            print "valid IPv6 packet"
            packet = IPv6(data)
        except struct.error:
            print "not an IPv6 packet"
            log.msg("not an IPv6 packet")

        # assert that the destination IPv6 address matches our address
        if packet.dst != self.local_addr:
            log.msg("packet destination doesn't match our vpn destination")

        # write the IPv6 packet to our consumer
        print "writing to consumer now"
        self.consumer.write(data)

    def logPrefix(self):
        return 'OnionProducer'

    # IPushProducer
    def pauseProducing(self):
        print "pauseProducing"

    def resumeProducing(self):
        print "resumeProducing"

    def stopProducing(self):
        print "stopProducing"
