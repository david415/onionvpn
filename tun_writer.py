#!/usr/bin/env python

# External modules
from twisted.internet import main, interfaces, reactor
from zope.interface import implements
import os
from scapy.all import IP, TCP, hexdump
import binascii
from zope.interface import implementer
from twisted.python import log

# Internal modules
from tun_factory import TUNFactory
from tun_reader import TUNPacketProducer, TUN_TestConsumer


@implementer(interfaces.IConsumer)
class TUNPacketConsumer(object):


    def __init__(self, tunDevice):
        self.tunDevice     = tunDevice
        self.packets       = []
        self.producer      = None


    def registerProducer(self, producer, streaming):
        log.msg("TUNPacketConsumer: registerProducer")
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("TUNPacketConsumer: unregisterProducer")
        self.producer.stopProducing()

    def write(self, packet):
        log.msg("TUNPacketConsumer: write: packet len %s" % len(packet))
        self.tunDevice.write(packet)

    def logPrefix(self):
        return 'TUNPacketConsumer'



