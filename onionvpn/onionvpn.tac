from twisted.application import service
from service import OnionVPNService

application = service.Application("OnionVPN")
onionVPNService = OnionVPNService('tun0', "xqo5qmr7ton4pwie", "my_onion_key_dir")
onionVPNService.setServiceParent(application)
