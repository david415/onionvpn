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

class HushPacketMTUException(Exception):
     pass


class HushPacketConsumer(object):

     implements(interfaces.IConsumer)
     mtu = 50

     def __init__(self, dest_ip):
          self.dest_ip          = dest_ip
          self.ip_packet_writer = IPPacketWriter(dest_ip)
          self.producer         = None

     def registerProducer(self, producer, streaming):
          assert self.producer is None
          assert streaming is True

          self.producer = producer
          self.ip_packet_writer.start()

     def unregisterProducer(self):
          assert self.producer is not None
          self.producer.stop_reading()
          self.ip_packet_writer.stop()

     def write(self, packet):
          self.ip_packet_writer.write(self.encodeHushPacket(packet))

     def encodeHushPacket(self, packet):

          if len(packet) > HushPacketConsumer.mtu:
               raise HushPacketMTUException

          id, seq, ack, window = struct.unpack_from('!HIIH', packet[:12])
          tcp_extended_header = packet[12:]

          ip  = IP(dst=self.ip_dest, id=id)
          tcp = TCP(dport   = port_dest, 
                    flags   = 'S',
                    seq     = seq,
                    ack     = ack,
                    window  = window,
                    options = [('MSS',tcp_extended_header)])

          encoded_packet = ip/tcp
          return encoded_packet


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


def main():
     dest_ip = '127.0.0.1'
     ip  = IP(dst=dest_ip)
     tcp = TCP(dport   = 688, 
               flags   = 'S',
               seq     = 32456,
               ack     = 32456,
               window  = 32456,
               options = [('MSS',binascii.unhexlify("DEADBEEFCAFE"))])

     packet = str(ip/tcp)
     hexdump(packet)
     print "pkt len %s" % len(packet)

     tunFactory   = TUNFactory(remote_ip = '10.1.1.1',
                               local_ip  = '10.1.1.2',
                               netmask   = '255.255.255.0',
                               mtu       = 1500)

     tunDevice    = tunFactory.buildTUN()

     hush_consumer = HushPacketConsumer(dest_ip)
     tun_reader   = TUNPacketProducer(tunDevice, hush_consumer)

     reactor.run()

if __name__ == '__main__':
     main()
