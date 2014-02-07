

from twisted.application import service
from ponyVPN_service import PonyVPNService


application    = service.Application("PonyVPN")
ponyVPNService = PonyVPNService(tun_local_ip        = '10.1.1.6',
                                      tun_remote_ip       = '10.1.1.5',
                                      tun_netmask         = '255.255.255.0',
                                      tun_mtu             = 1000,
                                      udp_remote_ip       = '',
                                      udp_remote_port     = 1194,
                                      udp_local_port      = 1194,
                                      udp_local_ip        = '')


ponyVPNService.setServiceParent(application)
