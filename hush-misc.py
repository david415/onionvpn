
"""
Implementation of the Hush protocol.
"""


from nflog_cffi import NFLOG, NFWouldBlock
from twisted.internet import reactor, protocol, defer
from twisted.python import log


class NFLogReader(object):

    def __init__(self, fd, nflogIter, nflogProto):
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


class NFLogProtocol(Protocol):
    def __init_(self, factory):
        self.factory = factory

    def dataReceived(pkt):
        self.factory.handlePacket(pkt)

    def connectionLost(self, reason):
        self.factory.nflogReader.connectionLost(self, reason)
        return reason


class NFLogFactory(Factory):
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

    def __init__(self):
        pass

    def startService():
        service.Service.startService(self)

    def stopService():
        service.Service.stopService(self)

    def privilegedStartService():
        pass




class HushOutgoing(protocol.Protocol):

    def __init__(self, hush):
        self.hush = hush

    def connectionMade(self):
        self.hush.otherConn=self

    def connectionLost(self, reason):
        self.hush.transport.loseConnection()

    def dataReceived(self,data):
        self.hush.write(data)

class HushIncoming(protocol.Protocol):

    def __init__(self):
        pass


class Hush(protocol.Protocol):

    def __init__(self, logging=None):
        self.logging=logging

    def connectionMade(self):
        self.buf=""
        self.otherConn=None

    def dataReceived(data):
        self.otherConn.write(data)

    def connectionLost(self, reason):
        self.otherConn.transport.loseConnection()

    def makeReply(self,reply):
        self.transport.write(reply)


class HushTransport(transport.Transport):
    
    def __init_(self):
        pass

    def write(data):
        pass

    def writeSequence(data):
        pass

    def loseConnection():
        pass

    def getPeer():
        pass
