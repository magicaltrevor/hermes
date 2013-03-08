"""This is an example plugin to test the plugin system for development against as well as to document the various requirements for writing plugins"""

"""First up you should import the databases, util and the models"""
import hermes.lib.util as Util
from datetime import datetime
from hermes.engines.databases import *
from hermes.engines.HermesModels import * 
import simplejson
"""Any additional libraries you might need from lib or services can be put in here as well"""

"""Next, define a class for your plugin. The class should be the plugin name."""
class Plugindemo():
    """At this point you will need 2 methods, an execute method and a cron method. Execute method is for services(commandline scripts, api, etc.) to fire off your plugin functionality.
       The cron method is for executing your plugin functionality via the hermes cron system. You can choose to have an init function or you can do it via @classmethods. Each method should
       contain at least the following params: client, map, legend, and params. Both legend and params can be optional but you should include it in the function anyway (see HermesModels documentation for more info on these params)"""

    def __init__(self, client, map=None, legend=None, params=None):
        """Example of initializing the class with the required params"""
        self.client = client
        self.map = map
        self.legend = legend
        self.params = params
        
        if hasattr(self, 'logging') is False : 
            self._set_logging()
        
        self.logging.info("Running Plugindemo")
        
    @classmethod
    def _set_logging(self):
        print "inited the logging"
        self.logging = logging.getLogger('plugins.Plugindemo')
        
    
    @classmethod    
    def cron(self, client, map=None, legend=None, params=None, event=None):
        """Under normal circumstances you wouldn't create a @classmethod when you have an __init__ function however for the sake of demonstration we are doing it here.
           This is the cron method. This is the method you would call if creating an event that uses this plugin. Code here should be designed to run autonomously and 
           require no input from the user. This will execute at specified times based on the Event created."""
        """In Cron, this function's output will go to the Cron log since it captures stdout so you can put debug info here or you can add your own logging mechanism.
           As this is automated there is no way to pass arbitrary params here."""
        myParams = simplejson.loads(params)
        print "Cron: Client = %s, Data = %s, Map = %s, Legend = %s, Timestamp = %s" % (client, map, legend, params, datetime.now().isoformat())
        print "From: %s, To: %s, Message: %s" % (myParams['from'], myParams['to'], myParams['message'])
        
    def arbitraryMethod(self, arbitrary):
        """You can also have your own arbitrary functions here that get called by other methods. They do not have the same requirements."""
        arbitrary = "This data is %s" % arbitrary
        return arbitrary
    
    def listSystemItems(self, id=None, itemType=None, template=False):
        """
            This function is required if the System has Multiple Maps Enabled.
            
            No params to get the main list or pass in parameters according to the following:
            Id       : to get a specific item details from list,
            Type     : like course/program if needed
            Template : to display the template (legend) or the column names (map)
            
        """
        data = {}
        
        return data