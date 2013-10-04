#!/usr/bin/env python

from nflog_cffi import NFLOG, NFWouldBlock
from twisted.internet import main, interfaces, reactor
from zope.interface import implements


class NFLogPacketProducer(object):

    implements(interfaces.IPushProducer, interfaces.IReadDescriptor)

    def __init__(self, dropPrivCallback = None, queues = (0,1), nflog_kwargs=dict(), consumer=None):
        super(NFLogPacketProducer, self).__init__()

        self.nflog_kwargs = nflog_kwargs
        self.queues       = queues

        self.nflog        = NFLOG().generator(self.queues, **self.nflog_kwargs)
        self.fd           = self.nflog.next()
        consumer.registerProducer(self, streaming=True)
        self.consumer = consumer
        self.start_reading()

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

    def fileno(self):
        return self.fd

    def connectionLost(self, reason):
        self.stop_reading()
        self.consumer.unregisterProducer()

        # BUG: must close the netlink_filter socket?
        # Does this work?
        # self.fd.close()
        return reason

    def doRead(self):
        packet = self.nflog.next()
        while True:
            self.consumer.write(packet)
            packet = self.nflog.send(True)
            if packet is NFWouldBlock: break

    def logPrefix(self):
        return 'NFLogPacketProducer'



class NFLOG_TestConsumer(object):

    implements(interfaces.IConsumer)

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
        print "packet len %s" % len(packet)


# Steps to perform test:
# 1. iptables -A INPUT -p tcp --dport 669 -j NFLOG
# 2. start this program
# 3. telnet localhost 669
# 4. observe this program prints the packet length

def main():
    consumer = NFLOG_TestConsumer()
    producer = NFLogPacketProducer(consumer = consumer)


    reactor.run()
 
if __name__ == "__main__":
    main()

