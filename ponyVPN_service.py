#!/usr/bin/env python

# External modules
from twisted.internet import reactor
from twisted.application import service
import pytun

# Internal modules
from tun_protocol import TunProducerConsumer
from icmp_readerwriter import ICMPReaderWriter
from twisted.pair.tuntap import TuntapPort


class PonyVPNService(service.Service):

    def __init__(self, 
                 tun_name    = None,
                 remote_ip   = None,
                 local_ip    = None):

        self.tun_name    = tun_name
        self.remote_ip   = remote_ip
        self.local_ip    = local_ip

    def startService(self):

        tun_protocol = TunProducerConsumer()

        icmp_ConsumerProducer = ICMPReaderWriter(
            consumer    = tun_protocol, 
            local_ip    = self.local_ip,
            remote_ip   = self.remote_ip)

        tun_protocol.setConsumer(icmp_ConsumerProducer)

        tun = TuntapPort(b"tun0", tun_protocol, reactor=reactor)

        tun.startListening()
        icmp_ConsumerProducer.start()

    def stopService(self):
        pass


