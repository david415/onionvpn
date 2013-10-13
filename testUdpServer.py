#!/usr/bin/env python

# External modules
from twisted.internet import main, interfaces, reactor
from zope.interface import implementer
from twisted.application import service
from scapy.all import IP, UDP

# Internal modules
from udp_consumer_producer import UDP_ConsumerProxy, UDP_ProducerProxy


class TestUdpServerService(service.Service):

    def __init__(self, udp_local_ip    = None,
                 udp_local_port        = None,
                 udp_remote_ip         = None,
                 udp_remote_port       = None):

        self.udp_local_ip    = udp_local_ip
        self.udp_local_port  = udp_local_port

        self.udp_remote_ip   = udp_remote_ip
        self.udp_remote_port   = udp_remote_port



    def startService(self):
        test_consumer     = TestConsumer()

        udp_ProducerProxy = UDP_ProducerProxy(consumer = test_consumer,
                                              host     = self.udp_local_ip,
                                              port     = self.udp_local_port)




        reactor.addReader(udp_ProducerProxy)
        reactor.run()


@implementer(interfaces.IPullProducer)
class TestProducer(object):

    def __init__(self, consumer=None, packet=None):

        self.consumer     = consumer
        self.packet = packet

        consumer.registerProducer(self, streaming=True)

    def resumeProducing(self):
        assert self.consumer is not None

        for x in range(3):
            self.consumer.write(self.packet)

    def stopProducing(self):
        pass

    def start_reading(self):
        self.resumeProducing()


@implementer(interfaces.IConsumer)
class TestConsumer(object):

    def __init__(self):
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
        print "TestConsumer: packet: %s" % packet




application          = service.Application("HushVPN")
testUdpServerService = TestUdpServerService(udp_local_ip        = '0.0.0.0',
                                            udp_local_port      = 1194,
                                            udp_remote_ip       = '192.155.82.5',
                                            udp_remote_port     = 1194)

testUdpServerService.setServiceParent(application)

