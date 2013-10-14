

from twisted.application import service
from hushVPN_service import HushVPNService


application    = service.Application("HushVPN")
hushVPNService = HushVPNService(tun_local_ip        = '10.1.1.6',
                                      tun_remote_ip       = '10.1.1.5',
                                      tun_netmask         = '255.255.255.0',
                                      tun_mtu             = 1000,
                                      udp_remote_ip       = '',
                                      udp_remote_port     = 1194,
                                      udp_local_port      = 1194,
                                      udp_local_ip        = '')


hushVPNService.setServiceParent(application)
