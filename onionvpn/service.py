
from twisted.internet import reactor
from twisted.application import service
from twisted.internet.endpoints import serverFromString
from twisted.pair.tuntap import TuntapPort

from tun_protocol import TunProducerConsumer
from tcp_frame_producer import TcpFrameProducer, PersistentSingletonFactory
from ipv6_onion_consumer import IPv6OnionConsumer
from convert import convert_onion_to_ipv6


class OnionVPNService(service.Service):

    def __init__(self, tun_name, onion, onion_key_dir):
        # XXX should accept a tor_control_address argument
        self.tun_name = tun_name
        self.onion = onion
        self.onion_key_dir = onion_key_dir

    def startService(self):
        local_addr = convert_onion_to_ipv6(self.onion)

        tun_protocol = TunProducerConsumer()
        frame_producer_protocol = TcpFrameProducer(local_addr,
                                                   consumer=tun_protocol)
        persistentFactory = PersistentSingletonFactory(frame_producer_protocol)

        ipv6_onion_consumer = IPv6OnionConsumer(reactor)
        tun_protocol.setConsumer(ipv6_onion_consumer)

        # listen to onion virtport 8060 for onioncat compatibility
        onion_endpoint = serverFromString(
            reactor,
            "onion:8060:hiddenServiceDir=%s" % self.onion_key_dir
        )

        d = onion_endpoint.listen(persistentFactory)

        def display(result):
            print result
        d.addCallback(display)

        tun = TuntapPort(self.tun_name, tun_protocol, reactor=reactor)
        tun.startListening()

        return d

    def stopService(self):
        pass
