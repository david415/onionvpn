#!/usr/bin/env python

# External modules
from twisted.application import service
import pytun


# Internal modules
from tun_factory import TUNFactory
from tun_reader import TUNPacketProducer, TUN_TestConsumer
from tun_writer import TUN_TestProducer
from nflog_reader import NFLogPacketProducer, NFLOG_TestConsumer
from tun_writer import TUNPacketConsumer
from hush_reader import HushPacketProducer
from hush_writer import HushPacketConsumer


# iptables -A INPUT -p icmp -j NFLOG
# iptables -A INPUT -p icmp -j DROP



class HushVPNService(service.Service):

    def __init__(self, 
                 tun_local_ip  = None,
                 tun_remote_ip = None,
                 tun_netmask   = None,
                 mtu           = None,
                 nflog_dest_ip = None):

        self.tun_local_ip  = tun_local_ip
        self.tun_remote_ip = tun_remote_ip
        self.tun_netmask   = tun_netmask
        self.mtu           = mtu
        self.nflog_dest_ip = nflog_dest_ip


    def startService(self):

        self.tunDevice = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        
        self.tunDevice.addr    = self.tun_local_ip
        self.tunDevice.dstaddr = self.tun_remote_ip
        self.tunDevice.netmask = self.tun_netmask
        self.tunDevice.mtu     = self.mtu

        # TODO: drop priveleges after bring up interface
        self.tunDevice.up()
        
        self.hush_consumer = HushPacketConsumer(self.nflog_dest_ip)
        self.tun_producer  = TUNPacketProducer(self.tunDevice, self.hush_consumer) 

        self.tun_consumer  = TUNPacketConsumer(self.tunDevice)
        self.hush_producer = HushPacketProducer(consumer = self.tun_consumer)

    def stopService(self):
        pass


