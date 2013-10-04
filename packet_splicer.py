#!/usr/bin/env python

# External modules
from twisted.internet import main, interfaces, reactor
from zope.interface import implements
from socket import socket, AF_INET, SOCK_RAW, gethostbyname, gethostname, IPPROTO_RAW, SOL_IP, IP_HDRINCL
from scapy.all import TCP, IP, hexdump
import binascii
import struct

# Internal modules
from tun_factory import TUNFactory
from tun_reader import TUNPacketProducer, TUN_TestConsumer
from tun_writer import TUN_TestProducer
from nflog_reader import NFLogPacketProducer, NFLOG_TestConsumer


class SplicedPacketProducer(object):

    implements(interfaces.IPushProducer, interfaces.IConsumer)

    def __init__(self, consumer=None, input_producer_factory=None, mtu=None):
        super(SplicedPacketProducer, self).__init__()

        self.mtu            = mtu
        self.producer       = None
        self.input_producer = input_producer_factory.buildProducer(self)

        consumer.registerProducer(self, streaming=True)
        self.consumer       = consumer
        self.start_reading()

   # IPushProducer section
    def pauseProducing(self):
        self.input_producer.stop_reading()

    def resumeProducing(self):
        self.input_producer.start_reading()

    def stopProducing(self):
        connDone = failure.Failure(main.CONNECTION_DONE)
        self.connectionLost(connDone)
        return connDone

    def start_reading(self):
        self.input_producer.start_reading()

   # IConsumer section
    def registerProducer(self, producer, streaming):
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.start_reading()

    def unregisterProducer(self):
        assert self.producer is not None
        self.producer.stop_reading()

    def write(self, packet):
        if len(packet) > self.mtu:
            spliced_packets = []
            for i in range(0, len(packet), self.mtu):
                spliced_packet = packet[i:i+self.mtu]
                self.consumer.write(spliced_packet)
        else:
            self.consumer.write(packet)


