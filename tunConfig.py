#!/usr/bin/env python

from pytun import TunTapDevice

TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2


class tunDevice():

    def __init__(self, remote_ip = None, local_ip = None, netmask = None, mtu = None, user_id = None, dropPrivCallback = None):
        self.tun         = TunTapDevice()
        self.tun.addr    = local_ip
        self.tun.dstaddr = remote_ip
        self.tun.netmask = netmask
        self.tun.mtu     = mtu

        if user_id is not None:
            fcntl.ioctl(tun, TUNSETOWNER, userid)
            if dropPrivCallback is not None:
                dropPrivCallback()
