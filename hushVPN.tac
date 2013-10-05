

from twisted.application import service
from hushVPN_service import HushVPNService


def getHushVPNService():
    return HushVPNService(tun_local_ip = '10.1.1.6',
                   tun_remote_ip       = '10.1.1.5',
                   tun_netmask         = '255.255.255.0',
                   mtu                 = 500,
                   nflog_dest_ip       = '127.0.0.1')

application    = service.Application("HushVPN")
hushVPNService = getHushVPNService()
hushVPNService.setServiceParent(application)
