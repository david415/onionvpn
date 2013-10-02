
"""
Implementation of the NFLog protocol.
"""


from nflog_cffi import NFLOG, NFWouldBlock
from twisted.internet import reactor, protocol, defer
from twisted.application import service
from twisted.python import log


class NFLogReader(object):

    def __init__(self, fd, nflogIter):
        self.fd           = fd
        self.nflogIter    = nflogIter
        self.nflogProto   = nflogProto

    def fileno(self):
        return self.fd

    def connectionLost(self, reason):
        reactor.removeReader(self)
        return reason

    def doRead(self):
        pkt = self.nflogIter.next()
        while True:
            self.nflogProto.dataReceived(pkt)
            pkt = self.nflogIter.send(True)
            if pkt is NFWouldBlock: break

    def logPrefix(self):
        return 'nflog'


class NFLogProtocol(protocol.BaseProtocol):
    def __init_(self, factory):
        self.factory = factory

    def startFactory(self):
        pass


    def dataReceived(pkt):
        self.factory.handlePacket(pkt)

    def connectionLost(self, reason):
        self.factory.nflogReader.connectionLost(self, reason)
        return reason

class NFLogFactory(protocol.Factory):
    protocol = NFLogProtocol

    def buildProtocol(handlePacket = None, queues = (0,1), nflog_kwargs=dict()):
        self.nflog_kwargs = nflog_kwargs
        self.queues       = queues
        self.handlePacket = handlePacket
        self.nflog_iter   = NFLOG().generator(self.queues, **self.nflog_kwargs)
        self.fd           = self.nflog.next()

        self.nflogProto   = Factory.buildProtocol(self, handlePacket)

        self.nflogReader  = NFLogReader(handlePacket = self.handlePacket,
                                        fd           = self.factory.fd,
                                        nflogIter    = self.nflogIter,
                                        nflogProto   = self.nflogProto)

        return self.nflogProto


    def clientConnectionFailed(self, connector, reason):
        print 'Failed to connect to:', connector.getDestination()


class NFLogService(service.Service):

    def __init__(self, nflog_reader, nflog_factory):
        self.nflog_reader = nflog_reader
        self.nflog_factory = nflog_factory



    def startService():
        service.Service.startService(self)

        

    def stopService():
        service.Service.stopService(self)

    def setServiceParent(parent):
        pass


    def main():
        application = service.Application("HushVPN")
        top_service = service.MultiService()

        nflog_factory = NFLogFactory(nflog_service)
        nflog_reader  = NFLogReader()

        nflog_service = NFLogService(nflog_reader, nflog_factory)
        nflog_service.setServiceParent(top_service)        

if __name__ == '__main__':
    main()
