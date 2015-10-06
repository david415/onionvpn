from zope.interface import implementer

from twisted.internet import interfaces
from twisted.python import log
from twisted.protocols.basic import Int16StringReceiver
from twisted.internet.protocol import Factory

class PersistentSingletonFactory(Factory):
    def __init__(self, protocol):
        self.protocol = protocol

    def buildProtocol(self, addr):
        return self.protocol

@implementer(interfaces.IPushProducer)
class TcpFrameProducer(Int16StringReceiver, object):
    def __init__(self, local_addr, consumer = None):
        super(TcpFrameProducer, self).__init__()
        self.local_addr = local_addr
        self.consumer = consumer

    def stringReceived(self, data):
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
        log.msg("pauseProducing")

    def resumeProducing(self):
        log.msg("resumeProducing")

    def stopProducing(self):
        log.msg("stopProducing")
