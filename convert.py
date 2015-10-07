import socket
import base64


def convert_ipv6_to_onion(ipv6_addr):
    packet = socket.inet_pton(socket.AF_INET6, ipv6_addr)
    return base64.b32encode(packet[:10]).lower()


def convert_onion_to_ipv6(onion):
    raw_onion = base64.b32decode(onion, True)
    local_addr = raw_onion + "BEEFCO"
    return socket.inet_ntop(socket.AF_INET6, local_addr)
