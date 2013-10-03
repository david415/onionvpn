#!/usr/bin/env python

from twisted.internet import main
from twisted.internet import reactor
from socket import socket, AF_INET, SOCK_RAW, gethostbyname, gethostname, IPPROTO_RAW, SOL_IP, IP_HDRINCL

from scapy.all import TCP, IP, hexdump
import binascii

class HushWriter(object):

     def __init__(self, dest_ip):
          self.dest_ip = (dest_ip, 0)
          self.socket  = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
          self.socket.setsockopt(SOL_IP, IP_HDRINCL, 1)
          self.socket.setblocking(0)
          self.packets = []

     def addPacket(self, packet):
          if len(self.packets) == 0:
               reactor.addWriter(self)
          self.packets.append(packet)

     def fileno(self):
          return self.socket.fileno()

     def connectionLost(self, reason):
          reactor.removeWriter(self)

     def doWrite(self):
          if len(self.packets) > 0:
               print "writing"
               self.socket.sendto(self.packets.pop(0), self.dest_ip)
          if len(self.packets) == 0:
               reactor.removeWriter(self)

     def logPrefix(self):
         return 'HushWriter'



def main():
    ip  = IP(dst="10.1.1.1")
    tcp = TCP(dport   = 688, 
              flags   = 'S',
              seq     = 32456,
              ack     = 32456,
              window  = 32456,
              options = [('MSS',binascii.unhexlify("DEADBEEFCAFE"))])

    packet = str(ip/tcp)
    hexdump(packet)
    print "pkt len %s" % len(packet)
    
    hush = HushWriter('10.1.1.1')
    
    for x in range(3):
        hush.addPacket(packet)

    reactor.run()

if __name__ == '__main__':
    main()
