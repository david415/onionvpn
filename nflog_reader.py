#!/usr/bin/env python

from nflog_cffi import NFLOG, NFWouldBlock
from twisted.internet import main
from twisted.internet import reactor


class NFLOGReader(object):

    def __init__(self, dropPrivCallback = None, handlePacket = None, queues = (0,1), nflog_kwargs=dict()):
        """Setup the NFLOG generator. """

        self.nflog_kwargs = nflog_kwargs
        self.queues       = queues
        self.handlePacket = handlePacket
        self.nflog        = NFLOG().generator(self.queues, **self.nflog_kwargs)
        self.fd           = self.nflog.send(None)
       

        if dropPrivCallback is not None:
            dropPrivCallback()

        reactor.addReader(self)

    def fileno(self):
        return self.fd

    def connectionLost(self, reason):
        reactor.removeReader(self)

    def doRead(self):
        self.handlePacket(self.nflog.next())
        # BUG: broken
#        while True:
#            pkt = self.nflog.send(True)
#            if pkt is NFWouldBlock:
#                break
#            self.handlePacket(pkt)

    def logPrefix(self):
        return 'nflog'


def main():
    
    def printPacketLen(p):
        print len(p)

    nflog = NFLOGReader(handlePacket=printPacketLen)

    reactor.run()

if __name__ == '__main__':
    main()
