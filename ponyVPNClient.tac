

from twisted.application import service
from ponyVPN_service import PonyVPNService


application    = service.Application("PonyVPN")
ponyVPNService = PonyVPNService(tun_local_ip        = '10.1.1.6',
                                      tun_remote_ip       = '10.1.1.5',
                                      tun_netmask         = '255.255.255.0',
                                      tun_mtu             = 1400,
                                      remote_ip       = '192.168.1.2',
                                      local_ip        = '192.168.2.1')


ponyVPNService.setServiceParent(application)
