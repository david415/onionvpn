
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, interfaces
from zope.interface import implementer
from twisted.python import log
import sys
import socket
from scapy.all import IP


@implementer(interfaces.IConsumer, interfaces.IPushProducer)
class UDP_ConsumerProducerProxy(DatagramProtocol, object):

    def __init__(self, consumer = None, local_ip = None, local_port = None, remote_ip = None, remote_port = None):
        super(UDP_ConsumerProducerProxy, self).__init__()

        self.local_ip    = local_ip
        self.local_port  = local_port
        self.remote_ip   = remote_ip
        self.remote_port = remote_port
        self.consumer    = consumer
        self.producer    = None


    def startProtocol(self):
        self.transport.connect(self.remote_ip, self.remote_port)
        self.consumer.registerProducer(self, streaming=True)

    def datagramReceived(self, packet, (host, port)):
        print "datagramReceive: packet from %s %s" % (host, port)
        print "datagramReceived: packet summary: " + IP(packet).summary()
        print "datagramReceived: packet len: %s" % len(packet)
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

    # IConsumer section
    def write(self, packet):
        print "UDP IConsumer write: packet summary " + IP(packet).summary()
        self.transport.write(packet)

    def registerProducer(self, producer, streaming):
        log.msg("UDP_ConsumerProducerProxy: registerProducer")
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("UDP_ConsumerProducerProxy: unregisterProducer")
        assert self.producer is not None
        self.producer.stopProducing()

    def logPrefix(self):
        return 'UDP_ConsumerProducerProxy'



