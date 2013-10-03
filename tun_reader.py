#!/usr/bin/env python

# External modules
from twisted.internet import main
from twisted.internet import reactor
import os
from scapy.all import IP, TCP, hexdump
import struct
import binascii

# Internal modules
from tunConfig import tunDevice


class TUNReader(object):

    def __init__(self, tun, mtu, handlePacket):
        self.tun          = tun
        self.mtu          = mtu
        self.handlePacket = handlePacket
        self.fd           = os.dup(tun.tun.fileno())

        # BUG: drop privs after bring up interface
        self.tun.tun.up()


    def connectionLost(self, reason):
        # BUG: we should remove the tun device
        # unless someone is still using it...
        reactor.removeReader(self)

    def fileno(self):
        return self.fd

    def doRead(self):
        packet = self.tun.tun.read(self.mtu)
        self.handlePacket(packet)

    def logPrefix(self):
        return 'TUNReader'



def main():

    def printPacketLen(p):
        hexdump(p)
        print "pkt len %s" % len(p)

    mtu = 1500
    mytun = tunDevice(remote_ip = '10.1.1.1',
                    local_ip  = '10.1.1.2',
                    netmask   = '255.255.255.0',
                    mtu       = mtu)
    
    tun_reader = TUNReader(mytun, handlePacket=printPacketLen, mtu = mtu)
    reactor.addReader(tun_reader)

    reactor.run()

if __name__ == '__main__':
    main()
