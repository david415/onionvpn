#!/usr/bin/env python

from twisted.internet import main, interfaces, reactor
from twisted.python import log
from zope.interface import implementer

import socket
from scapy.all import IP, ICMP, Raw
import struct


@implementer(interfaces.IReadDescriptor, interfaces.IConsumer, interfaces.IPushProducer)
class ICMPReaderWriter(object):

    def __init__(self, consumer = None, local_ip = None, remote_ip = None):

        self.local_ip = local_ip
        self.remote_ip = remote_ip

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.socket.bind(('0.0.0.0', 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.socket.setblocking(0)

        self.consumer = consumer
        self.producer = None


    def start(self):
        reactor.addReader(self)

    def stop(self):
        reactor.removeReader(self)

    def logPrefix(self):
        return 'ICMPReaderWriter'

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")

    def resumeProducing(self):
        log.msg("resumeProducing")

    def stopProducing(self):
        log.msg("stopProducing")


    # IConsumer section

    def write(self, packet):
        log.msg("write")
        icmp_packet = IP(dst=self.remote_ip)/ICMP()/Raw(load=str(packet))
        self.socket.sendto(str(icmp_packet), (self.remote_ip,0))

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer")
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.resumeProducing()

    def unregisterProducer(self):
        log.msg("unregisterProducer")
        assert self.producer is not None
        self.producer.stopProducing()


    # IReadWriteDescriptor

    def fileno(self):
        return self.socket.fileno()

    def connectionLost(self, reason):
        log.msg("connectionLost")
        reactor.removeReader(self)
        return reason

    def doRead(self):
        log.msg("doRead")

        # XXX
        packet_str = self.socket.recv(65565)
        outer_packet = IP(packet_str)

        if ICMP in outer_packet:
            inner_packet = outer_packet.load
            self.consumer.write(str(inner_packet))
