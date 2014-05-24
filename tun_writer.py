#!/usr/bin/env python

# External modules
from twisted.internet import interfaces
from zope.interface import implementer
from twisted.python import log
import pytun
import os

import struct
from scapy.all import IP


@implementer(interfaces.IConsumer)
class TUNPacketConsumer(object):


    def __init__(self, tunDevice):
        self.tunDevice     = tunDevice
        self.producer      = None
        self.fd            = os.dup(tunDevice.fileno())

    def logPrefix(self):
        return 'TUNPacketConsumer'

    # IConsumer

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        self.producer.stopProducing()

    def write(self, packet):
        log.msg("write")
        try:
            IP(packet)
        except struct.error:
            log.msg("TunPacketConsumer: write: not a valid IP packet")
        else:
            self.tunDevice.write(packet)
