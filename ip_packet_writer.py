#!/usr/bin/env python

# External modules
from twisted.internet import main, interfaces, reactor
from zope.interface import implements
from socket import socket, AF_INET, SOCK_RAW, gethostbyname, gethostname, IPPROTO_RAW, SOL_IP, IP_HDRINCL
from scapy.all import TCP, IP, hexdump
import binascii
import struct

# Internal modules
from tun_factory import TUNFactory
from tun_reader import TUNPacketProducer, TUN_TestConsumer
from tun_writer import TUN_TestProducer


class IPPacketWriter(object):

     implements(interfaces.IWriteDescriptor)

     def __init__(self, dest_ip):
          self.dest_ip = (dest_ip, 0)
          self.socket  = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
          self.socket.setsockopt(SOL_IP, IP_HDRINCL, 1)
          self.socket.setblocking(0)
          self.packets = []

     def start(self):
          reactor.addWriter(self)

     def stop(self):
          reactor.removeWriter(self)

     def write(self, packet):
          if len(self.packets) == 0:
               reactor.addWriter(self)
          self.packets.append(packet)

     def fileno(self):
          return self.socket.fileno()

     def connectionLost(self, reason):
          reactor.removeWriter(self)
          return reason

     def doWrite(self):
          if len(self.packets) > 0:
               self.socket.sendto(self.packets.pop(0), self.dest_ip)
          if len(self.packets) == 0:
               reactor.removeWriter(self)

     def logPrefix(self):
         return 'IPPacketWriter'
