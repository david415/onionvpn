
onionvpn
========

onionvpn utilizes a tun device to create a virtual-public-network... which
transports ipv6; using tor onion services as the transport. onionvpn does not
provide a cryptographic transport like most VPNs (virtual-private-networks).

onionvpn is now compatible with onioncat! i was able to verify this on my own system
but i did not find any onioncat ipv6 addresses in the wild that would respond to pings.


network configuration
---------------------

Here's how i setup my TUN device in linux:

Firstly... I use my tor process to generate onion service key material.
Then I retrieve that onion address and use python to convert it to an
IPv6 address with our onioncat/onionvpn 6byte prefix like so:

    >>> def convert_onion_to_ipv6(onion):
    ...     raw_onion = base64.b32decode(onion, True)
    ...     # onioncat compatibility for addressing...
    ...     local_addr = binascii.a2b_hex("fd87d87eeb43") + raw_onion
    ...     return socket.inet_ntop(socket.AF_INET6, local_addr)
    ...
    >>> convert_onion_to_ipv6('22u7o5ej47o5z7jf')
    'fd87:d87e:eb43:d6a9:f774:89e7:dddc:fd25'


This will be our <ONION-AS-IPv6-ADDR> variable.
Create the tun device:

    ip tuntap add dev tun0 mode tun user <USER> group <GROUP>
    ip address add scope global <ONION-AS-IPv6-ADDR> peer fd87:d87e:eb43::/48 dev tun0
    ifconfig tun0 up


Then add a static route for our subnet:

    ip route add fd87:d87e:eb43::/48 dev tun0


installing
----------

onionvpn depends on txtorcon and scapy. you can install via pip like this:

    pip install git+https://github.com/david415/onionvpn.git


running
-------

onionvpn usage:

    (onion-virtenv)user@debian-python2:~$ onionvpn -h
    WARNING: Failed to execute tcpdump. Check it is installed and in the PATH
    WARNING: No route found for IPv6 destination :: (no default route?)
    usage: onionvpn [-h] onion onion_endpoint tun

    onionvpn - onion service tun device adapter

    positional arguments:
      onion           Local onion address
      onion_endpoint  Twisted endpoint descriptor string for the onion service
                      which listens on onion virtport 8060
      tun             tun device name

    optional arguments:
      -h, --help      show this help message and exit


For example, run it like this:

    onionvpn 22u7o5ej47o5z7jf tcp:interface=127.0.0.1:8060 tun0


onion_endpoint must be specified such that it produces a Twisted
endpoint object capable of listening to the onion service on virtport 8060...
The above TCP server endpoint requires you to run tor with the appropriate onion service
configuration, like this:

    HiddenServiceDir /var/lib/tor/onionvpn
    HiddenServicePort 8060 127.0.0.1:8060


This above configuration will work... but you can also use txtorcon's onion service endpoint:

    onionvpn 22u7o5ej47o5z7jf onion:8060:hiddenServiceDir=/home/human/onion_key tun0


That above endpoint results in the txtorcon endpoint launching a new tor instance;
you can instead specify a tor control port:

    onionvpn 22u7o5ej47o5z7jf onion:8060:controlPort=/var/run/tor/control:hiddenServiceDir=/home/human/onion_key tun0


The above onion: endpoint string will work under debian based linux distros if the user belongs
to the debian-tor group.
