#!/usr/bin/env python

from twisted.internet import main
from twisted.internet import reactor
import struct
import fcntl
import os
import subprocess

# constants
TUNSETIFF   = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN     = 0x0001
IFF_TAP     = 0x0002
IFF_NO_PI   = 0x1000


class tunReader(object):

    def __init__(self, remote_ip, local_ip, handlePacket=None, userid=None, dropPrivCallback = None):
        self.remote_ip = remote_ip
        self.local_ip  = local_ip
        self.tun       = open('/dev/net/tun', 'r+b')

        # BUG: choose available name
        self.name      = 'tun0'

        ifr = struct.pack('16sH', self.name, IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.tun, TUNSETIFF, ifr)

        if userid is not None:
            fcntl.ioctl(tun, TUNSETOWNER, userid)
            if dropPrivCallback is not None:
                dropPrivCallback()

        self.config()
        print "constructor done"

    def config(self):
        # BUG: do this in a thread or something
        # BUG: mode? is this correct?
        #runcommand("ip add %s remote %s local %s" % (self.name, self.remote_ip, self.local_ip), shell=False)
        pass

    def connectionLost(self, reason):
        # BUG: we should remove the tun device
        reactor.removeReader(self)

    def fileno(self):
        return self.tun.fileno()

    def doRead(self):
        packet = os.read(self.tun.fileno(), 2048)
        self.handlePacket(packet)


def main():
    tunReader(remote_ip='10.1.1.1', local_ip='10.1.1.2', userid=None, dropPrivCallback=None)

    reactor.run()

if __name__ == '__main__':
    main()
