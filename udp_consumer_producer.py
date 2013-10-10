
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, interfaces
from zope.interface import implementer
from twisted.python import log
import sys
import socket


@implementer(interfaces.IConsumer, interfaces.IWriteDescriptor)
class UDP_ConsumerProxy(object):

    def __init__(self, host = None, port = None):
        self.host     = host
        self.port     = port
        self.producer = None
        self.packets  = []

        self.socket   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)

    # IConsumer section

    def write(self, packet):
        log.msg("write: enqueuing packet len: %s" % len(packet))
        if len(self.packets) == 0:
            reactor.addWriter(self)
        self.packets.append(packet)

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.start_reading()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        assert self.producer is not None
        self.producer.stop_reading()

    # IWriteDescriptor section

    def fileno(self):
        return self.socket.fileno()

    def connectionLost(self, reason):
        reactor.removeWriter(self)
        return reason

    def doWrite(self):
        log.msg("doWrite called")
        if len(self.packets) > 0:
            self.socket.sendto(self.packets.pop(0), (self.host, self.port))
        if len(self.packets) == 0:
            reactor.removeWriter(self)

    def logPrefix(self):
        return 'UDP_ConsumerProxy'




@implementer(interfaces.IPushProducer, interfaces.IReadDescriptor)
class UDP_ProducerProxy(object):

    def __init__(self, consumer=None, host=None, port=None):

        self.host      = host
        self.port      = port
        self.consumer  = consumer

        self.socket    = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.setblocking(0)

        log.msg("calling consumer.registerProducer")
        consumer.registerProducer(self, streaming=True)

    def start_reading(self):
        reactor.addReader(self)

    def stop_reading(self):
        reactor.removeReader(self)

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")
        reactor.removeReader(self)

    def resumeProducing(self):
        log.msg("resumeProducing")
        reactor.addReader(self)

    def stopProducing(self):
        connDone = failure.Failure(main.CONNECTION_DONE)
        self.connectionLost(connDone)

    # IReadDescriptor
    def doRead(self):
        packet, address = self.socket.recvfrom(1500)
        log.msg("doRead: packet len %s from %s" % (len(packet), address))
        self.consumer.write(packet)
        
    def fileno(self):
        return self.socket.fileno()
        
    def connectionLost(self, reason):
        self.stop_reading()
        self.consumer.unregisterProducer()
        self.socket.close()
        return reason

    def logPrefix(self):
        return 'UDP_ProducerProxy'

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")
        pass

    def resumeProducing(self):
        log.msg("resumeProducing")
        pass

    def stopProducing(self):
        log.msg("stopProducing")
        pass

    def start_reading(self):
        log.msg("start_reading")
        pass

    def stop_reading(self):
        log.msg("stop_reading")
        pass

    def logPrefix(self):
        return 'UDP_ProducerProxy'


