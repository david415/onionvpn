onionvpn
========

Network Configuration
---------------------

Here's how i setup my TUN device in linux:

    # ip tuntap add dev tun0 mode tun user <USER> group <GROUP>
    # ip address add scope global fe80::216:3eff:fe5e:face peer fe80::216:3eff:fe5e:beef dev tun0
    # ifconfig tun0 up

Deleting TUN interfaces:

    # ip tuntap del dev tun0 mode tun

I was then able to send packets to the tun device with a ping like so:

    #ping6 -I tun0 fe80::216:3eff:fe5e:beef

Dependencies
------------

    # git clone https://github.com/david415/onionvpn.git && cd onionvpn
    # pip install -r requirements.txt

Running

    # twistd -ny onionvpn.tac
