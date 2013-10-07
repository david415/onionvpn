
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, interfaces
from zope.interface import implementer



@implementer(interfaces.IConsumer)
class UDP_ConsumerProxy(DatagramProtocol, object):

    def __init__(self, host, port):
        self.host     = host
        self.port     = port
        self.producer = None

    def registerProducer(self, producer, streaming):
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.start_reading()

    def unregisterProducer(self):
        assert self.producer is not None
        self.producer.stop_reading()

    def write(self, packet):
        self.transport.write(packet, (self.host, self.port))



@implementer(interfaces.IPushProducer)
class UDP_ProducerProxy(DatagramProtocol, object):

    def __init__(self, consumer=None):
        super(UDP_ProducerProxy, self).__init__()

        self.consumer  = consumer
        consumer.registerProducer(self, streaming=True)

    def datagramReceived(self, packet, (host, port)):
        self.consumer.write(packet)


    # IPushProducer

    def pauseProducing(self):
        pass

    def resumeProducing(self):
        pass

    def stopProducing(self):
        pass

    def start_reading(self):
        pass

    def stop_reading(self):
        pass


