
import os, pwd, grp

from convert import convert_onion_to_ipv6


def generate_tun_linux_shell_code(onion):
    """
    generate_tun_linux_shell_code creates shell code to be run as root,
    it creates and configures a tun device with an ipv6 address derived
    from the onion address.
    """
    ipv6_address = convert_onion_to_ipv6(onion)
    tun_device = "tun0"
    user = pwd.getpwuid( os.getuid() ).pw_name
    gid = pwd.getpwnam(user).pw_gid
    group = grp.getgrgid(gid).gr_name
    shell_codes = """
ip tuntap add dev %s mode tun user %s group %s
ip address add scope global %s peer fd87:d87e:eb43::/48 dev %s
ifconfig %s up
    """ % (tun_device, user, group, ipv6_address, tun_device, tun_device)
    print "# your onion converted to ipv6 address is:"
    print "# %s" % (onion,)
    print shell_codes
