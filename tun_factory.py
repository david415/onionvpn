#!/usr/bin/env python

import pytun

class TUNFactory():

    def __init__(self, remote_ip = None, local_ip = None, netmask = None, mtu = None, user_id = None, dropPrivCallback = None):

        self.local_ip    = local_ip
        self.remote_ip   = remote_ip
        self.netmask     = netmask
        self.mtu         = mtu

    def buildTUN(self):
        self.tunDevice = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        
        self.tunDevice.addr    = self.local_ip
        self.tunDevice.dstaddr = self.remote_ip
        self.tunDevice.netmask = self.netmask
        self.tunDevice.mtu     = self.mtu

        return self.tunDevice

