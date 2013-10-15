#!/usr/bin/env python

# External modules
from twisted.internet import interfaces
from zope.interface import implementer
from twisted.python import log
import pytun
from scapy.all import IP


@implementer(interfaces.IConsumer)
class TUNPacketConsumer(object):


    def __init__(self, tunDevice):
        self.tunDevice     = tunDevice
        self.producer      = None

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        self.producer.stopProducing()

    def write(self, packet):
        #log.msg(IP(packet).summary())

        if len(packet) < 40:
            #log.msg("not forwarding small packet")
            return

        try:
            self.tunDevice.write(packet)
        except pytun.Error as e:
            log.msg("TUNPacketConsumer: pytun.Error: %s" % e)

    def logPrefix(self):
        return 'TUNPacketConsumer'



