#!/usr/bin/env python

# External modules
from twisted.internet import main
from twisted.internet import reactor
from twisted.internet import main, interfaces, reactor
from zope.interface import implementer
import os
from scapy.all import IP, TCP, hexdump
import struct
import binascii

# Internal modules
from tun_factory import TUNFactory


class TUN_Producer_Factory(object):

    def __init__(self, tunDevice):
        self.tunDevice = tunDevice

    def buildProducer(self, consumer=None):
        return TUNPacketProducer(self.tunDevice, consumer)



@implementer(interfaces.IReadDescriptor, interfaces.IPushProducer)
class TUNPacketProducer(object):


    def __init__(self, tunDevice, consumer=None):
        super(TUNPacketProducer, self).__init__()

        self.tunDevice    = tunDevice
        self.mtu          = tunDevice.mtu
        self.fd           = os.dup(tunDevice.fileno())

        consumer.registerProducer(self, streaming=True)
        self.consumer     = consumer

        reactor.addReader(self)

    def start_reading(self):
        """Register with the Twisted reactor."""
        reactor.addReader(self)

    def stop_reading(self):
        """Unregister with the Twisted reactor."""
        reactor.removeReader(self)

    def pauseProducing(self):
        reactor.removeReader(self)

    def resumeProducing(self):
        self.start_reading()

    def stopProducing(self):
        connDone = failure.Failure(main.CONNECTION_DONE)
        self.connectionLost(connDone)

    def connectionLost(self, reason):
        self.stop_reading()
        self.consumer.unregisterProducer()
        self.tunDevice.close()
        self.tunDevice.down()
        return reason

    def fileno(self):
        return self.fd

    def doRead(self):
        packet = self.tunDevice.read(self.tunDevice.mtu)
        print "doRead: packet len %s" % len(packet)
        self.consumer.write(packet)

    def logPrefix(self):
        return 'TUNPacketProducer'




@implementer(interfaces.IConsumer)
class TUN_TestConsumer(object):


    def __init__(self):
        self.producer = None

    def registerProducer(self, producer, streaming):
        assert self.producer is None
        assert streaming is True

        self.producer = producer
        self.producer.start_reading()

    def unregisterProducer(self):
        assert self.producer is not None
        self.producer.stop_reading()

    def write(self, packet):
        print "TUN_TestConsumer: packet len %s" % len(packet)


def main():

    tunFactory   = TUNFactory(remote_ip = '10.1.1.1',
                              local_ip  = '10.1.1.2',
                              netmask   = '255.255.255.0',
                              mtu       = 1500)

    tunDevice    = tunFactory.buildTUN()
    tun_consumer = TUN_TestConsumer()
    tun_reader   = TUNPacketProducer(tunDevice, tun_consumer)

    reactor.addReader(tun_reader)
    reactor.run()

if __name__ == '__main__':
    main()
