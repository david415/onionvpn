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
from tun_reader import TUNPacketProducer, TUNReaderFactory, TUN_TestConsumer
from tun_writer import TUN_TestProducer
from ip_packet_writer import IPPacketWriter
from packet_splicer import SplicedPacketProducer


class HushPacketMTUException(Exception):
     pass


class HushPacketConsumer(object):

     implements(interfaces.IConsumer)
     mtu = 600

     def __init__(self, dest_ip, dest_port):
          self.dest_ip          = dest_ip
          self.dest_port        = dest_port
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
          ip  = IP(dst    = self.dest_ip)
          tcp = TCP(dport = self.dest_port)
          encoded_packet = str(ip/tcp/packet)
          return encoded_packet


def main():
     dest_ip      = '127.0.0.1'
     dest_port    = 6900

     tunFactory   = TUNFactory(remote_ip = '10.1.1.1',
                               local_ip  = '10.1.1.2',
                               netmask   = '255.255.255.0',
                               mtu       = 1500)

     tunDevice          = tunFactory.buildTUN()
     hush_consumer      = HushPacketConsumer(dest_ip, dest_port)
     tun_reader_factory = TUNReaderFactory(tunDevice)
     
     spliced_packet_relay = SplicedPacketProducer(
          consumer               = hush_consumer,
          input_producer_factory = tun_reader_factory,
          mtu                    = 50)


     reactor.run()

if __name__ == '__main__':
     main()
