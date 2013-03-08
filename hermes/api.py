#!/usr/bin/env python

import web
import os, sys
import urllib
import logging
import time
libpath = '/usr/local/lib/python2.7/site-packages/'
#sys.path.insert(0,libpath)
#abspath = os.path.abspath(__file__).replace(os.path.basename(__file__),"")
#sys.path.append(abspath)
#os.chdir(abspath)
#
#
## add this file location to sys.path
#cmd_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#if cmd_folder not in sys.path:
#     sys.path.insert(-1, cmd_folder)
#     sys.path.insert(-1, cmd_folder + "/engines")
#     sys.path.insert(-1, cmd_folder + "/plugins")
#     sys.path.insert(-1, cmd_folder + "/lib")
#     sys.path.insert(-1, cmd_folder + "/services")
from hermes.services.HermesWebServices import HermesWebServices as API
import hermes.lib.util as Util
from hermes.engines.Cron import *

conf = Util.load_conf()
Util.init_logging()


# set port and IP to listen for alerts
# these are inhereited from the conf file
sys.argv = [conf['api_listen_ip'],conf['api_port']]

# debug mode
web.config.debug = conf['server_debug']

#load valid urls to listen to for http calls
urls = (
    '/api/(.+)', 'api'
)
urls = urls + ('/pluginapi/(.+)', 'pluginapi')

"""
	For debugging uncomment the following
"""
urls = urls + ('/test/', 'testClass')
"""
	End of debug
"""

app = web.application(urls, globals())

class api:
    '''
    This class handles api calls /api/client/<module>/<method>/<params>
    '''
    def GET(self,data):
        client, module, method, methodParams = data.split('/')
        logger = logging.getLogger('hermes.api.get')
        logger.info("%s GET api query\n%s" % (client, data))
        #logger.info("GET: %s" % client)
        apicall = API(client=client, methodParams=urllib.unquote_plus(methodParams))
        apicall.Api(module, method, urllib.unquote_plus(methodParams))
        print "Finished all initializations, running job and returning results"
        returnJson = apicall.fulljson()
        apicall = ''
        return returnJson
    
    def POST(self, urlParams):
        data = web.data()
        client, module, method = urlParams.split('/')
        logger = logging.getLogger('hermes.api.post')
        logger.info("%s POST api query\n%s%s" % (client, urlParams, urllib.unquote_plus(data)))
        
        apicall = API(client=client, methodParams=urllib.unquote_plus(data))
        apicall.Api(module, method, urllib.unquote_plus(data))
        returnJson =  apicall.fulljson()
        apicall = ''
        return returnJson
    
class pluginapi:
    '''
    This class handles api requests for plugins /pluginapi/client/plugin/<arbitrary function>/<params>
    '''
    def GET(self,data):
        pluginFile, plugin, client, module, method, methodParams = data.split('/')
        logger = logging.getLogger('hermes.pluginapi.get')
        logger.info("Receiving a GET api query\n%s" % (data))     
        apicall = API(client, plugin, pluginFile, urllib.unquote_plus(methodParams))
        apicall.Api(module, method, urllib.unquote_plus(methodParams))
        logger.info("Finished all initializations, running job and returning results")
        returnJson =  apicall.fulljson()
        apicall = ''
        return returnJson
    
    def POST(self, urlParams):
        data = web.data()
        logger = logging.getLogger('hermes.pluginapi.post')
        logger.info("Receiving a POST api query\n%s%s" % (urlParams, urllib.unquote_plus(data)))
        pluginFile, plugin, client, module, method = urlParams.split('/')
        apicall = API(client, plugin, pluginFile, urllib.unquote_plus(data))
        apicall.Api(module, method, urllib.unquote_plus(data))
        returnJson =  apicall.fulljson()
        apicall = ''
        return returnJson
              
class testClass:
    '''
    This class is for displaying a page to test the api
    '''
    def GET(self, data=''):
        logger = logging.getLogger('hermes.api.testclass.get')
        logger.info("Receiving a GET test query\n%s" % (data))
        hello = web.template.render('templates')
        return hello.testPage('hello', Util.load_client_conf())



if __name__ == "__main__":
    app.run()
else:
    application = app.wsgifunc()
