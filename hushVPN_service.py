#!/usr/bin/env python

# External modules
from twisted.internet import reactor
from twisted.application import service
import pytun

# Internal modules
from tun_reader import TUNPacketProducer
from tun_writer import TUNPacketConsumer
from udp_consumer_producer import UDP_ConsumerProducerProxy



class HushVPNService(service.Service):

    def __init__(self, 
                 tun_local_ip    = None,
                 tun_remote_ip   = None,
                 tun_netmask     = None,
                 tun_mtu         = None,
                 udp_remote_ip   = None,
                 udp_remote_port = None,
                 udp_local_ip    = None,
                 udp_local_port  = None):

        self.tun_local_ip    = tun_local_ip
        self.tun_remote_ip   = tun_remote_ip
        self.tun_netmask     = tun_netmask
        self.tun_mtu         = tun_mtu
        self.udp_remote_ip   = udp_remote_ip
        self.udp_remote_port = udp_remote_port
        self.udp_local_ip    = udp_local_ip
        self.udp_local_port  = udp_local_port


    def startService(self):

        self.tunDevice = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        
        self.tunDevice.addr    = self.tun_local_ip
        self.tunDevice.dstaddr = self.tun_remote_ip
        self.tunDevice.netmask = self.tun_netmask
        self.tunDevice.mtu     = self.tun_mtu

        # TODO: drop priveleges after bringing up interface
        self.tunDevice.up()

        # UDP <-> TUN
        tun_consumer = TUNPacketConsumer(self.tunDevice)

        udp_ConsumerProducerProxy = UDP_ConsumerProducerProxy(
            consumer    = tun_consumer, 
            local_ip    = self.udp_local_ip,
            local_port  = self.udp_local_port,
            remote_ip   = self.udp_remote_ip,
            remote_port = self.udp_remote_port)

        tun_producer = TUNPacketProducer(self.tunDevice, consumer = udp_ConsumerProducerProxy)


        reactor.listenUDP(self.udp_local_port, udp_ConsumerProducerProxy)
        reactor.addReader(tun_producer)


    def stopService(self):
        pass


