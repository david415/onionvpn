onionvpn
========

here's how i setup my tun device in linux:

ip tuntap add dev tun0 mode tun user human group human
ip address add scope global fe80::216:3eff:fe5e:face peer fe80::216:3eff:fe5e:beef dev tun0

i was then able to send packets to the tun device with a ping like so:
ping6 -I tun2 fe80::216:3eff:fe5e:beef

Dependencies
------------

- Twisted
- Scapy



