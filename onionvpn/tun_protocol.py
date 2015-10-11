#!/usr/bin/env python

from twisted.internet import interfaces
from twisted.pair.ip import IPProtocol
from twisted.python import log

from zope.interface import implementer
import struct
from scapy.all import IPv6


@implementer(interfaces.IPushProducer, interfaces.IConsumer)
class TunProducerConsumer(IPProtocol):

    def __init_(self):
        # IConsumer
        self.producer = None

    def setConsumer(self, consumer):
        # IPushProducer
        consumer.registerProducer(self, streaming=True)
        self.consumer = consumer

    # XXX correct?
    def logPrefix(self):
        return 'TunProducerConsumer'

    # IPProtocol
    def datagramReceived(self, datagram, partial=None):
        print "TunProducerConsumer datagramReceived"
        # XXX should we keep this assertion?
        # TuntapPort expects our function signature to contain a
        # `partial` argument but always sets it's value to zero.
        # https://twistedmatrix.com/trac/browser/tags/releases/twisted-15.4.0/twisted/pair/tuntap.py#L338
        assert partial == 0
        try:
            packet = IPv6(datagram)
            assert packet.version == 6
        except struct.error:
            log.msg("not an IPv6 packet")
        self.consumer.write(datagram)

    # IPushProducer

    def pauseProducing(self):
        print "pauseProducing"

    def resumeProducing(self):
        print "resumeProducing"

    def stopProducing(self):
        print "stopProducing"

    # IConsumer
    def write(self, packet):
        print "datagramReceived write"
        # Write from TUN to the Onion consumer
        self.transport.write(packet)

    def registerProducer(self, producer, streaming):
        print "registerProducer"
        assert streaming is True
        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        print "unregisterProducer"
        self.producer.stopProducing()
