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

    tunFactory   = TUNFactory(remote_ip = '10.1.1.5',
                              local_ip  = '10.1.1.6',
                              netmask   = '255.255.255.0',
                              mtu       = 1500)

    tunDevice    = tunFactory.buildTUN()


    tun_consumer = TUNPacketConsumer(tunDevice)
    reactor.addWriter(tun_consumer)

    hush_producer = HushPacketProducer(consumer = tun_consumer)

 
    reactor.run()
 
if __name__ == "__main__":
    main()
