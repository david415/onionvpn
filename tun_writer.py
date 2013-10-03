#!/usr/bin/env python

# External modules
from twisted.internet import main
from twisted.internet import reactor
import os

# Internal modules
from tunConfig import tunDevice


class TUNWriter(object):

    def __init__(self, tun):
        self.tun     = tun
        self.packets = []
        self.fd      = os.dup(tun.tun.fileno())


    def connectionLost(self, reason):
        # BUG: we should remove the tun device
        # unless someone is still using it...
        reactor.removeWriter(self)

    def fileno(self):
        return self.fd

    def addPacket(self, packet):
        if len(self.packets) == 0:
            reactor.addWriter(self)
        self.packets.append(packet)

    def doWrite(self):
        if len(self.packets) > 0:
            self.tun.tun.write(self.packets.pop(0))
        if len(self.packets) == 0:
            reactor.removeWriter(self)

    def logPrefix(self):
        return 'TUNWriter'



def main():

    ip  = IP(dst="10.1.1.1")
    tcp = TCP(dport   = 2600, 
              flags   = 'S',
              seq     = 32456,
              ack     = 32456,
              window  = 32456,
              options = [('MSS',binascii.unhexlify("DEADBEEFCAFE"))])

    packet = str(ip/tcp)

    def printPacketLen(p):
        print len(p)


    mytun = tunDevice(remote_ip = '10.1.1.1',
                      local_ip  = '10.1.1.2',
                      netmask   = '255.255.255.0',
                      mtu       = 1500)

    tunwriter = TUNWriter(mytun.tun)
    tunwriter.addPacket(packet)
    reactor.addWriter(tunwriter)
    reactor.run()

if __name__ == '__main__':
    main()
