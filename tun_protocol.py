#!/usr/bin/env python

from zope.interface import implementer
from twisted.pair.tuntap import TuntapPort
from twisted.pair.ip import IPProtocol
from twisted.internet import reactor, protocol, interfaces
from twisted.python import log, failure

from scapy.all import hexdump, IP, TCP
import struct


@implementer(interfaces.IPushProducer, interfaces.IConsumer)
class TunProducerConsumer(IPProtocol):

    def __init_(self):

        # IConsumer
        self.producer = None

    def setConsumer(self, consumer):
        # IPushProducer
        consumer.registerProducer(self, streaming=True)
        self.consumer = consumer

    # IPProtocol

    def datagramReceived(self, datagram, partial=None):
        assert partial == 0

        try:
            IP(datagram)
        except struct.error:
            pass
        else:
            self.consumer.write(datagram)

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")

    def resumeProducing(self):
        log.msg("resumeProducing")

    def stopProducing(self):
        log.msg("stopProducing")

   # IConsumer

    def write(self, packet):

        # wtf. fix weird bug
        if len(packet) != 56:
            self.transport.write(packet)

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        self.producer.stopProducing()
