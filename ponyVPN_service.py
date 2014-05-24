#!/usr/bin/env python

# External modules
from twisted.internet import reactor
from twisted.application import service
import pytun

# Internal modules
from tun_reader import TUNPacketProducer
from tun_writer import TUNPacketConsumer
from icmp_readerwriter import ICMPReaderWriter



class PonyVPNService(service.Service):

    def __init__(self, 
                 tun_local_ip    = None,
                 tun_remote_ip   = None,
                 tun_netmask     = None,
                 tun_mtu         = None,
                 remote_ip   = None,
                 local_ip    = None):

        self.tun_local_ip    = tun_local_ip
        self.tun_remote_ip   = tun_remote_ip
        self.tun_netmask     = tun_netmask
        self.tun_mtu         = tun_mtu
        self.remote_ip   = remote_ip
        self.local_ip    = local_ip

    def startService(self):
        print "startService"

        self.tunDevice = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        self.tunDevice.addr    = self.tun_local_ip
        self.tunDevice.dstaddr = self.tun_remote_ip
        self.tunDevice.netmask = self.tun_netmask
        self.tunDevice.mtu     = self.tun_mtu

        # TODO: drop priveleges after bringing up interface
        self.tunDevice.up()

        # ICMP <-> TUN
        tun_consumer = TUNPacketConsumer(self.tunDevice)

        icmp_ConsumerProducer = ICMPReaderWriter(
            consumer    = tun_consumer, 
            local_ip    = self.local_ip,
            remote_ip   = self.remote_ip)

        tun_producer = TUNPacketProducer(self.tunDevice, consumer = icmp_ConsumerProducer)

        reactor.addReader(tun_producer)
        icmp_ConsumerProducer.start()

    def stopService(self):
        pass


