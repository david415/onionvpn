from zope.interface import implementer

from twisted.internet import interfaces
from twisted.protocols.basic import Int16StringReceiver
from twisted.internet.protocol import Protocol, Factory

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
        self.target_protocol.dataReceived(data)

@implementer(interfaces.IPushProducer)
class TcpFrameProducer(Int16StringReceiver, object):
    def __init__(self, local_addr, consumer = None):
        super(TcpFrameProducer, self).__init__()
        print "TcpFrameProducer init"
        self.local_addr = local_addr
        self.consumer = consumer

    def stringReceived(self, data):
        print "stringReceived"
        # assert that it's an IPv6 packet
        try:
            packet = IP(data)
            assert packet.version == 6
        except struct.error:
            log.msg("not an IPv6 packet")

        # assert that the destination IPv6 address matches our address
        if packet.dst != self.local_addr:
            log.msg("packet destination doesn't match our vpn destination")

        # write the IPv6 packet to our consumer
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
