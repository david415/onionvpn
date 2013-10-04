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

class HushPacketProducer(object):

    implements(interfaces.IPushProducer, interfaces.IConsumer)
 
    def __init__(self, consumer = None):
        super(HushPacketProducer, self).__init__()

        self.packets = []
        self.producer = None
        self.nflogProducer = NFLogPacketProducer(consumer = self)

        consumer.registerProducer(self, streaming=True)
        self.consumer     = consumer
        self.start_reading()

    # IPushProducer section
    def pauseProducing(self):
        self.nflogProducer.stop_reading()

    def resumeProducing(self):
        self.nflogProducer.start_reading()

    def stopProducing(self):
        connDone = failure.Failure(main.CONNECTION_DONE)
        self.connectionLost(connDone)
        return connDone

    def start_reading(self):
        self.nflogProducer.start_reading()

 
    # IConsumer section
    def registerProducer(self, producer, streaming):
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.start_reading()

    def unregisterProducer(self):
        assert self.producer is not None
        self.producer.stop_reading()

    def write(self, packet):
        # BUG: this line fucks shit up for some reason!?
        packet = self.decodeHushPacket(packet)
        self.consumer.write(packet)

    def decodeHushPacket(self, packet):
        ip_packet = IP(packet)
        tcp_packet = ip_packet[TCP]
        tcp_options = dict(tcp_packet.options)
        if tcp_options.has_key('MSS'):
            tcp_extended_header = tcp_options['MSS']
        else:
            raise HushPacketParseException

        decoded_packet = struct.pack('!HIIH', 
                                     ip_packet.id,
                                     tcp_packet.seq,
                                     tcp_packet.ack,
                                     tcp_packet.window) + str(tcp_extended_header)
        return decoded_packet

def main():
    consumer = NFLOG_TestConsumer()
    producer = HushPacketProducer(consumer = consumer)


    reactor.run()
 
if __name__ == "__main__":
    main()
