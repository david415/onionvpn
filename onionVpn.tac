
from twisted.application import service
from service import OnionVPNService

application = service.Application("OnionVPN")
onionVPNService = OnionVPNService('tun0', 9050, "my_onion_key_dir")
onionVPNService.setServiceParent(application)