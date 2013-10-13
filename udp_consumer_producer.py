
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, interfaces
from zope.interface import implementer
from twisted.python import log
import sys
import socket
from scapy.all import IP


@implementer(interfaces.IConsumer)
class UDP_ConsumerProxy(object, DatagramProtocol):

    def __init__(self, host = None, port = None):
        super(UDP_ConsumerProxy, self).__init__()

        self.host     = host
        self.port     = port
        self.producer = None

    # IConsumer section
    def write(self, packet):
        print "UDP IConsumer write: packet summary " + IP(packet).summary()
        self.transport.write(packet, (self.host, self.port))

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

    def logPrefix(self):
        return 'UDP_ConsumerProxy'



@implementer(interfaces.IPushProducer)
class UDP_ProducerProxy(object, DatagramProtocol):

    def __init__(self, consumer=None, host=None, port=None):
        super(UDP_ProducerProxy, self).__init__()

        self.host      = host
        self.port      = port
        self.consumer  = consumer

        log.msg("calling consumer.registerProducer")
        consumer.registerProducer(self, streaming=True)


    def datagramReceived(self, packet, (host, port)):
        print "datagramReceived: packet summary: " + IP(packet).summary()
        self.consumer.write(packet)

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")
        self.pause = True

    def resumeProducing(self):
        log.msg("resumeProducing")
        self.pause = False

    def stopProducing(self):
        log.msg("stopProducing")
        self.pause = True

    def logPrefix(self):
        return 'UDP_ProducerProxy'

