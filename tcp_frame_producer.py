from zope.interface import implementer

from twisted.internet import interfaces
from twisted.python import log
from twisted.protocols.basic import Int16StringReceiver


@implementer(interfaces.IPushProducer)
class TcpFrameProducer(Int16StringReceiver, object):
    def __init__(self, consumer = None):
        super(TcpFrameProducer, self).__init__()

    def stringReceived(self, data):
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
