#!/usr/bin/env python

import socket
from twisted.internet import reactor
from twisted.application import service
from twisted.pair.tuntap import TuntapPort

from tun_protocol import TunProducerConsumer
from tcp_frame_producer import TcpFrameProducer, PersistentSingletonFactory
from ipv6_onion_consumer import IPv6OnionConsumer
from twisted.internet.endpoints import serverFromString


class OnionVPNService(service.Service):

    def __init__(self, tun_name, tor_control_port, onion_key_dir):
        # XXX should accept a tor_control_address argument
        self.tun_name = tun_name
        self.tor_control_port = tor_control_port
        self.onion_key_dir = onion_key_dir

    def startService(self):
        tun_protocol = TunProducerConsumer()

        local_addr =  socket.inet_pton(socket.AF_INET6, "::1")        
        frame_producer_protocol = TcpFrameProducer(local_addr, consumer = tun_protocol)
        persistentFactory = PersistentSingletonFactory(frame_producer_protocol)

        ipv6_onion_consumer = IPv6OnionConsumer()
        tun_protocol.setConsumer(ipv6_onion_consumer)

        #onion_endpoint = serverFromString(reactor, "onion:80:controlPort=%s:hiddenServiceDir=%s" % (self.tor_control_port, self.onion_key_dir))
        onion_endpoint = serverFromString(reactor, "onion:80:hiddenServiceDir=%s" % self.onion_key_dir)

        d = onion_endpoint.listen(persistentFactory)
        def display(result):
            print result
        d.addCallback(display)

        tun = TuntapPort(self.tun_name, tun_protocol, reactor=reactor)
        tun.startListening()

        return d

    def stopService(self):
        pass
