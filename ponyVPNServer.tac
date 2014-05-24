
from twisted.application import service
from ponyVPN_service2 import PonyVPNService


application    = service.Application("PonyVPN")
ponyVPNService = PonyVPNService(tun_name        = 'tun0',
                                      remote_ip       = '192.168.2.2',
                                      local_ip        = '192.168.2.1')


ponyVPNService.setServiceParent(application)
