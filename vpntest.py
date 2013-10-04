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
from nflog_reader import NFLogPacketProducer, NFLOG_TestConsumer
from tun_writer import TUNPacketConsumer
from hush_reader import HushPacketProducer



def main():

    dest_ip      = '127.0.0.1'
    dest_port    = 6900

    tunFactory   = TUNFactory(remote_ip = '10.1.1.5',
                              local_ip  = '10.1.1.6',
                              netmask   = '255.255.255.0',
                              mtu       = 1500)
    tunDevice     = tunFactory.buildTUN()

    hush_consume  = HushPacketConsumer(dest_ip, dest_port)
    tun_reader_factory = TUNReaderFactory(tunDevice) 
    spliced_packet_relay = SplicedPacketProducer(
          consumer               = hush_consumer,
          input_producer_factory = tun_reader_factory,
          mtu                    = 50)


    tun_consumer = TUNPacketConsumer(tunDevice)
    reactor.addWriter(tun_consumer)

    hush_producer = HushPacketProducer(consumer = tun_consumer)

 
    reactor.run()
 
if __name__ == "__main__":
    main()
