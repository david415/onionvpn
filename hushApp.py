from twisted.application import service
import hush

application = service.Application("hushVPN")
serviceCollection = service.IServiceCollection(application)


hushService = hush.HushServer(port, key)
