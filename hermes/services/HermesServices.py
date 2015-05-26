from hermes.engines.databases import *
from hermes.engines.HermesModels import *
from hermes.engines.Cron import *
import hermes.lib.util as Util
conf = Util.load_conf()
import logging

class HermesServices():
    
    def __init__(self, client, plugin=None, pluginFile=None, methodParams={}):
        if plugin:
            print "Initializing hermes services with %s plugin" % plugin
            
            client_conf = Util.load_client_conf(client=client)
            
            name = "hermes.%s.%s" % (conf['plugin_prefix'], pluginFile)
            mod = __import__(name, globals(), locals(), [name], -1)
            
            #self.plugin = eval("mod.%s" % plugin)
            self.plugin = eval("mod.%s('%s',%s,%s,%s)" % (plugin, client, None, None, methodParams)) # #map, legend, methodParams
            
            #self.plugin = __import__('plugins', globals(), locals(), [str(plugin)], -1)
            logging.info("plugin details")
            logging.info("%s" % (dir(self.plugin)))
            
   		#self.plugin = eval(plugin)
        self.map = HermesMap
        self.legend = HermesLegend
        self.systems = HermesSystems
        self.dataStore = DataStore
        self.storeAttributes = StoreAttributes
        self.imported = DataStoreImported
        self.event = Event
        
    
    def initClient(self, client, debug='True'):
    	print "Initing client"
    	
    	#logging.info("initing client: %s" % client)
    	
    	# Set Client Name
    	self.map.client = client
    	self.legend.client = client
    	self.systems.client = client
    	self.dataStore.client = client
    	self.storeAttributes.client = client
    	self.imported.client = client
    	self.event.clientparam = client
    	
    	#if hasattr(self, 'plugin'):
        #    self.plugin.client = client
    	
    	# Get Both read and write connection
        client_connection = {}
    	client_connection['read'], client_connection['write'] = getConnectionsByClient(client)
    	
    	# Set Client Connection Attribute with a Dict of the Read and Write Connections
    	self.map.client_connection = client_connection
    	self.legend.client_connection = client_connection
    	self.systems.client_connection = client_connection
    	self.dataStore.client_connection = client_connection
    	self.storeAttributes.client_connection = client_connection
    	self.imported.client_connection = client_connection
    	
    	# Set SqlObject's Db Connection when initing the object
    	# inside the function it will adjust it to the read/write connection as needed
        self.map._connection = client_connection['read']
        self.map._connection.debug=debug
        self.legend._connection = client_connection['read']
        self.legend._connection.debug=debug
        self.systems._connection = client_connection['read']
        self.systems._connection.debug=debug
        self.dataStore._connection = client_connection['read']
        self.dataStore._connection.debug=debug
        self.storeAttributes._connection = client_connection['read']
        self.storeAttributes._connection.debug=debug
        self.imported._connection = client_connection['read']
        self.imported._connection.debug=debug
    	
        # Init the Logging
        self.map._set_logging()
        self.legend._set_logging()
        self.systems._set_logging()
        self.dataStore._set_logging()
        self.storeAttributes._set_logging()
        self.imported._set_logging()
        self.event._set_logging()
        
        #if hasattr(self, 'plugin'):
        #    self.plugin._set_logging()
    
    def buildRequestFromData(self, **data):
        self.params = data
        self.module = data['module']
        self.method = data['method']
        self.methodParams = data['methodParams']
        
    
    def executeRequest(self):
        if self.params:
            execution_string = 'self.%s.%s(**%s)' % (self.module, self.method, self.methodParams)
            logging.info("execution string: %s " % (execution_string))
            print execution_string
            self.clientTeardown()
            return eval(execution_string)
    
    def clientTeardown(self):
        client_connection = {}
        client_connection['read'], client_connection['write'] = getConnectionsByClient(self.client)
        client_connection['read'].expireAll()
        client_connection['write'].expireAll()
        
