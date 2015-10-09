onionvpn
========

Network Configuration
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

    # ip tuntap add dev tun0 mode tun user <USER> group <GROUP>
    # ip address add scope global <ONION-AS-IPv6-ADDR> peer fd87:d87e:eb43::/48 dev tun0
    # ifconfig tun0 up


Then add a static route for our subnet:

    ip route add fd87:d87e:eb43::/48 dev tun0


Next you must set your tun device name and onion address in the
`onionvpn.tac` file and then start the onionvpn like this:

    twistd -ny onionvpn1.tac -l -



Dependencies
------------

    # git clone https://github.com/david415/onionvpn.git && cd onionvpn
    # pip install -r requirements.txt

Running

    # twistd -ny onionvpn.tac
