
import socket
import string
import base64


def convert_ipv6_to_onion(ipv6_addr):
    packet = socket.inet_pton(socket.AF_INET6, ipv6_addr)
    return packet[:10]

def convert_onion_to_ipv6(onion):
    fields = string.split(onion, ".")
    assert len(fields) == 2
    raw_onion = base64.b32decode(fields[0], True)
    local_addr = raw_onion + "BEEFCO"
    return socket.inet_ntop(socket.AF_INET6, local_addr)
