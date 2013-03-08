from hermes.services.HermesServices import HermesServices
import hermes.lib.util as Util
import simplejson
conf = Util.load_conf()

class HermesWebServices(DigarcServices):
    
    def __init__(self, client, plugin=None, pluginFile=None, methodParams=None):
        DigarcServices.__init__(self, client, plugin, pluginFile, methodParams)
        #logging.info("init client: %s" % client)
        self.initClient(client)
        self.client = client
        
    def Api(self, module, method, methodParams):
        print "Initializing api"
        #db_connect = "self.%s" % module
        builder = '{"module":"%s", "method":"%s", "methodParams":%s}' % (module, method, methodParams)
        data = simplejson.loads(builder)
        print data
        self.buildRequestFromData(**data)
        print "Done"

    def fulljson(self):
        print "Fulljson"
        response = self.executeRequest()
        print response
        return simplejson.dumps(response)