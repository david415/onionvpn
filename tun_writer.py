#!/usr/bin/env python

# External modules
from twisted.internet import main
from twisted.internet import reactor

# Internal modules
from tunConfig import tunDevice


class tunWriter(object):

    def __init__(self, tun):
        self.tun     = tun
        self.packets = []
        reactor.addWriter(self)

    def connectionLost(self, reason):
        # BUG: we should remove the tun device
        # unless someone is still using it...
        reactor.removeReader(self)

    def fileno(self):
        return self.tun

    def addPacket(self, packet):
        self.packets.append(packet)

    def doWrite(self):
        if len(self.packets) > 0:
            self.tun.write(self.packets.pop(0))
        else:
            return

    def logPrefix(self):
        return 'tunWriter'



def main():

    ip  = IP(dst="127.0.0.1")
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

    tunwriter = tunWriter(mytun.tun, handlePacket=printPacketLen)


    tunwriter.addPacket(packet)

    reactor.run()

if __name__ == '__main__':
    main()
