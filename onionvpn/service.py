
from twisted.internet import reactor
from twisted.application import service
from twisted.internet.endpoints import serverFromString
from twisted.pair.tuntap import TuntapPort

from tun_protocol import TunProducerConsumer
from tcp_frame_producer import TcpFrameProducer, PersistentSingletonFactory
from ipv6_onion_consumer import IPv6OnionConsumer
from convert import convert_onion_to_ipv6


class OnionVPNService(service.Service):

    def __init__(self, tun_name, onion, onion_endpoint):
        self.tun_name = tun_name
        self.onion = onion
        self.onion_endpoint = onion_endpoint

    def startService(self):
        local_addr = convert_onion_to_ipv6(self.onion)

        tun_protocol = TunProducerConsumer()
        frame_producer_protocol = TcpFrameProducer(local_addr,
                                                   consumer=tun_protocol)
        persistentFactory = PersistentSingletonFactory(frame_producer_protocol)

        ipv6_onion_consumer = IPv6OnionConsumer(reactor)
        tun_protocol.setConsumer(ipv6_onion_consumer)

        # must listen to onion virtport 8060
        onion_endpoint = serverFromString(reactor,self.onion_endpoint)
        d = onion_endpoint.listen(persistentFactory)
        tun = TuntapPort(self.tun_name, tun_protocol, reactor=reactor)
        tun.startListening()
        return d

    def stopService(self):
        pass
