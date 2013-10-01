#!/usr/bin/env python

from nflog_cffi import NFLOG
from twisted.internet import main
from twisted.internet import reactor


class NFLOGReader(object):

    def __init__(self, dropPrivCallback = None, handlePacket = None):
        """Setup the NFLOG generator. """
        nflog_kwargs      = dict()
        queues            = 0, 1
        self.handlePacket = handlePacket
        self.nflog        = NFLOG().generator(queues, **nflog_kwargs)
        self.fd           = self.nflog.next()

        if dropPrivCallback is not None:
            dropPrivCallback()

        reactor.addReader(self)

    def fileno(self):
        return self.fd

    def connectionLost(self, reason):
        reactor.removeReader(self)

    def doRead(self):
        self.handlePacket(self.nflog.next())

    def logPrefix(self):
        return 'nflog'


def main():
    
    def printPacketLen(p):
        print len(p)

    nflog = NFLOGReader(handlePacket=printPacketLen)

    reactor.run()

if __name__ == '__main__':
    main()
