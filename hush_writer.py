#!/usr/bin/env python

from twisted.internet import main
from twisted.internet import reactor
from socket import socket, AF_INET, SOCK_RAW, gethostbyname, gethostname, IPPROTO_RAW, SOL_IP, IP_HDRINCL

from scapy.all import TCP, IP
import binascii

class HushWriter(object):

     def __init__(self, address):
          self.address = (address, 0)
          self.socket  = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
          self.socket.setsockopt(SOL_IP, IP_HDRINCL, 1)
          self.socket.setblocking(0)
          self.packets = []

          reactor.addWriter(self)

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
               self.socket.sendto(self.packets.pop(0), self.address)
          else:
               reactor.removeWriter(self)

     def logPrefix(self):
         return 'HushWriter'



def main():
    ip  = IP(dst="127.0.0.1")
    tcp = TCP(dport   = 2600, 
              flags   = 'S',
              seq     = 32456,
              ack     = 32456,
              window  = 32456,
              options = [('MSS',binascii.unhexlify("DEADBEEFCAFE"))])

    packet = str(ip/tcp)

    hush = HushWriter('127.0.0.1')
    
    for x in range(3):
        hush.addPacket(packet)

    reactor.run()

if __name__ == '__main__':
    main()
