#!/usr/bin/env python

# External modules
from twisted.internet import reactor
from twisted.application import service
import pytun


# Internal modules
from tun_factory import TUNFactory
from tun_reader import TUNPacketProducer
from tun_writer import TUNPacketConsumer
from udp_consumer_producer import UDP_ConsumerProxy, UDP_ProducerProxy
from tun_reader import TUN_Producer_Factory


# iptables -A INPUT -p icmp -j NFLOG
# iptables -A INPUT -p icmp -j DROP



class HushVPNService(service.Service):

    def __init__(self, 
                 tun_local_ip    = None,
                 tun_remote_ip   = None,
                 tun_netmask     = None,
                 tun_mtu         = None,
                 udp_remote_ip   = None,
                 udp_remote_port = None,
                 udp_local_port  = None):

        self.tun_local_ip    = tun_local_ip
        self.tun_remote_ip   = tun_remote_ip
        self.tun_netmask     = tun_netmask
        self.tun_mtu         = tun_mtu
        self.udp_remote_ip   = udp_remote_ip
        self.udp_remote_port = udp_remote_port
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

        tun_consumer           = TUNPacketConsumer(self.tunDevice)
        udp_ProducerProxy      = UDP_ProducerProxy(consumer = tun_consumer)


        udp_ConsumerProxy      = UDP_ConsumerProxy(self.udp_remote_ip, self.udp_remote_port)
        tun_producer           = TUNPacketProducer(self.tunDevice, consumer = udp_ConsumerProxy)


        reactor.listenUDP(self.udp_local_port, udp_ConsumerProxy)


    def stopService(self):
        pass


