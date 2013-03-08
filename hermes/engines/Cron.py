from datetime import datetime, timedelta
import optparse
from subprocess import Popen
import sys
import time
from hermes.plugins import *
import simplejson
import logging
import hermes.lib.util as Util
from sqlobject import *
from hermes.engines.databases import *
conf = Util.load_conf()
import gevent
#from hermes.hermesTaskMan import celery
from celery.contrib.methods import task
from celery.result import AsyncResult

"""A simple system for executing Hermes Plugins on a cron-like schedule"""

def main():
    """This function is for testing purposes only"""
    logging.info("main function called")
    cron = Cron()
    cron.run()
    
class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True

class Event(SQLObject):
    """Event for Cron. Legend, and params are optional. In the event that any of these params are not needed passing 0 or None will suffice"""
    _connection = getConnectionByDB(conf['hermes_write_database_db'],'write')
    class sqlmeta:
        table="events"
    mins = PickleCol()
    hours = PickleCol()
    days = PickleCol()
    months = PickleCol()
    label = StringCol(length=255)
    plugin = StringCol(length=255)
    pluginfile = StringCol(length=255)
    client = StringCol(length=255)
    map = IntCol()
    legend = IntCol()
    params = BLOBCol()
    lastrun = DateTimeCol(default=None)
    status = StringCol(length=255, default='')
    
    
    def _set_all_match(self):
        self.all_match = AllMatch()
    
    def _set_months(self, value):
        if value == '*':
            value = AllMatch()
        else:
            value = self.convert_to_set(value)
        self._SO_set_months(value)
        
    def _set_mins(self, value):
        if value == '*':
            value = AllMatch()
        else:
            value = self.convert_to_set(value)
        self._SO_set_mins(value)
    
    def _set_hours(self, value):
        if value == '*':
            value = AllMatch()
        else:
            value = self.convert_to_set(value)
        self._SO_set_hours(value)
    
    def _set_days(self, value):
        if value == '*':
            value = AllMatch()
        else:
            value = self.convert_to_set(value)
        self._SO_set_days(value)
        
    def _set_clientparam(self, value):
        self.logging.info("setting client param")
        self.clientparam = value
        
    def _set_legend(self, value):
        if value == 0:
            self._SO_set_legend(None)
        else:
            self._SO_set_legend(value)
    
    def _set_params(self, value):
        if value == 0 or value == None:
            self._SO_set_params(None)
        else:
            self._SO_set_params(value)
    
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.event')
        
    @classmethod
    def convert_to_set(self, obj):
        if isinstance(obj, (int,long)):
            return set([obj])
        if not isinstance(obj, set):
            obj = set(obj)
        return obj
    
    @classmethod
    def add_new_event(self, mins, hours, days, months, label, client, map, legend, params, plugin=None):
        """
            Add a New Cron Event
            
            ** Params:**
            
            For :
                - mins
                - hours
                - days
                - months
                
            You may pass a number or a list of numbers. Do not pass fractions
            
            - label  : name of event (ie: Map Name)
            - client : client name
            - map    : map id
            - legend : legend id (you may pass 0, but you must pass something)
            - params : these are passed into the plugin
            - plugin : plugin name (if none, grab plugin from the client config)
        """
        if mins == "*":
            mins = AllMatch()
        if hours == "*":
            hours = AllMatch()
        if days == "*":
            days = AllMatch()
        if months == "*":
            months = AllMatch()
        
        if plugin is None:
            # If plugin is not passed, grab from their config file
            client_conf = Util.load_client_conf(client=client)
            plugin = "%s" % (client_conf[client]['plugin'])
        
        self.logging.info("Cron Event: Adding New (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s )" % (mins, hours, days, months, label, client, map, legend, params, plugin))
        
        e = Event(mins=mins,hours=hours,days=days,months=months,label=label,plugin=plugin,client=client,map=map,legend=legend,params=params)
        return e
       
       
    @classmethod
    def saveEvent(self, mins, hours, days, months, label, map, params, legend=0, id=None, client=None, plugin=None, pluginfile=None):
        """
            Add / Update a Cron Event
            
            ** Params:**
            
            For :
                - mins
                - hours
                - days
                - months
                
            You may pass a number or a list of numbers. Do not pass fractions
            
            - label  : name of event (ie: Map Name)
            - client : client name
            - map    : map id
            - legend : legend id (you may pass 0, but you must pass something)
            - params : these are passed into the plugin
            - plugin : plugin name (if none, grab plugin from the client config)
        """
        
        if mins == "*":
            mins = AllMatch()
        if hours == "*":
            hours = AllMatch()
        if days == "*":
            days = AllMatch()
        if months == "*":
            months = AllMatch()
        
        if client == None:
            if hasattr(self, 'clientparam'):
                client = self.clientparam
        
        if client is not None:
        
            if plugin is None:
                # If plugin is not passed, grab from their config file
                client_conf = Util.load_client_conf(client=client)
                plugin = "%s" % (client_conf[client]['plugin'])
            
            self.logging.info("Cron Event: Saving Event (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s %s)" % (mins, hours, days, months, label, client, map, legend, params, plugin,  pluginfile))
            """
            eventDict = {
                        'mins'   : mins,
                        'hours'  : hours,
                        'days'   : days,
                        'months' : months,
                        'label'  : label,
                        'plugin' : plugin,
                        'pluginfile' : pluginfile,
                        'client' : str(client),
                        'map'    : map,
                        'legend' : legend,
                        'params' : params
                        }
            
            self.logging.info("Cron Event: Dict (%s)" % (eventDict))
            """
            
            if type(params) == dict :
            	params = simplejson.dumps(params)
            
            if id is not None and int(id) > 0 :
                
                existingEvent = Event.get(int(id))
                
                # if id passed, updated existing event
                existingEvent.set(mins=mins,hours=hours,days=days,months=months,label=label,plugin=plugin,pluginfile=pluginfile,client=client,map=map,legend=legend,params=params)
                
            else :
                # Add new Event
                existingEvent = Event(mins=mins,hours=hours,days=days,months=months,label=label,plugin=plugin,pluginfile=pluginfile,client=client,map=map,legend=legend,params=params)
                
            #logging.info("recently created event client: %s" % existingEvent.client)
            
            return self.formatEvent(existingEvent)
            
        return False
        
    
    def update_status(self, newStatus):
        task_id, status = self.status.split[':']
        status = newStatus
        newRecord = ':'.join([task_id, status])
        self.status = newRecord
    
    @classmethod
    def get_events_by_label(self, label):
        e = list(Event.select(Event.q.label == label))
        return e 
    
    @classmethod
    def get_event_jobStatus(self, status):
        """expects a celery job id and returns the status for the AsyncResult object"""
        from celery.result import AsyncResult
        r = AsyncResult(status)
        return r.status
    
    @classmethod
    def get_event_jobResult(self, status):
        """expects a celery job id and returns the result for the AsyncResult object"""
        from celery.result import AsyncResult
        r = AsyncResult(status)
        return r.result
    
    @classmethod
    def getEvent(self, id, client=None):
        
        if client == None:
            if hasattr(self, 'clientparam'):
                client = self.clientparam
                
        if client is None:
            return False
        
        existingEvent = Event.select(AND(
                                        Event.q.client == client,
                                        Event.q.id == int(id)
                                        ))[0]
        
        return self.formatEvent(existingEvent) 
        
    @classmethod
    def getEvents(self, client=None, label=None):
        """
            Return the Cron Events by the Client name
        """
        self.logging.info("getEvents")
        if client == None:
            if hasattr(self, 'clientparam'):
                client = self.clientparam
                self.logging.info("has client param it has: %s" % self.clientparam)
            else :
                self.logging.info("missing client param")
        
        query = None
        
        if client is not None:
            query = Event.q.client == client
        
        if label is not None:
            labelQuery = Event.q.label == label
            if query :
                query = AND(
                        query,
                        labelQuery)
            else :
                query = labelQuery
        
        self.logging.info("query: %s" % (Event.select(query)))
        
        #logging.info("results: %s" % (list(Event.select(query))))
        
        self.logging.info("found: %s" % (Event.select(query).count()))
        
        events = []
        for selectEvent in Event.select(query).orderBy(['label', 'map']):
            self.logging.info("selectEvent: %s " % (selectEvent.id))
            events.append(self.formatEvent(selectEvent))
        
        self.logging.info(events)
        
        return events
    
    def getStatus(self):
        return 
    
    @classmethod
    def deleteEvent(self, id, client=None):
        
        if client == None:
            if hasattr(self, 'clientparam'):
                client = self.clientparam
                
        if client is None:
            return False
        
        events = list(Event.select(AND(
                                        Event.q.client == client,
                                        Event.q.id == int(id)
                                        )))
        
        if len(events) > 0 :
            Event.delete(int(id))
            return True
        
        return False
    
    @classmethod
    def formatEvent(self, existingEvent):
        event = {
                'id' : existingEvent.id
                }
        
        self.logging.info("format event")

        for c in existingEvent.sqlmeta.columns :
            attribute = getattr(existingEvent, c)
            self.logging.info("attribute: %s" % (attribute))
            self.logging.info("type of attribute: %s" % (type(attribute)))
            if type(attribute) is set:
                attribute = list(attribute)
            
            elif type(attribute) is datetime:
                attribute = attribute.isoformat(' ')
            
            if isinstance(attribute, AllMatch):
                attribute = '*'
            
            event[c] = attribute

        return event
        
    def isRunning(self):
        if self.status == '':
            return False
        else:
            return self.status
        
    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute        in self.mins) and
                (t.hour          in self.hours) and
                (t.day           in self.days) and
                (t.month         in self.months))
        
    #@task()
    def runner(self):
        if self.status == '':
            print sys.path
            print "Running for client : %s" % self.client
            client_conf = Util.load_client_conf(client=self.client)
            if self.pluginfile != None:
                eventPluginFile = self.pluginfile
            else:
                 eventPluginFile = client_conf[self.client]['plugin_file']
            if self.plugin != None:
                 eventPlugin = self.plugin
            else:
                eventPlugin = client_conf[self.client]['plugin']
            try:
                if HermesCronServices:
                   service_handler = HermesCronServices(self.client, eventPlugin, eventPluginFile)
            except NameError:
               from hermes.services.HermesCronServices import HermesCronServices
               service_handler = HermesCronServices(self.client, eventPlugin, eventPluginFile)
            service_handler.initClient(self.client, self.map, self.legend, self.params, debug=True)
            plugin = service_handler.plugin
            print "params: %s" % (type(self.params))
            #self.process._set_logging()
            plugin.cron(client=self.client, map=self.map, legend=self.legend, params=self.params, event = self)
            self.lastrun = datetime.today()
            self.set(**{'lastrun' : self.lastrun})
            self.set(**{'status' : ''})
        else:
            return self.status
        
    @classmethod
    def runNow(self, id, taskID=None):
        """
        Runs a single event immediately
        """
        e = self.get(id)
        #try:
        #if not e.isRunning() == '':
        if not e.status == '':
            #job = e.runner.delay()
            e,set(**{'status' : 'running'})
            job = e.runner()
            #e.set(**{'status' : job.id})
            #return job.id
            return job.status
        else:
            #return e.isRunning()
            return "running"
    
    def check(self, t):
        self.logging.info("check start")
        if self.matchtime(t):
            # Avoid spawning another process if the last run didn't finish yet.
            #            if self.process:
            #                self.process.poll()
            #                if self.process.returncode != None:
            #                    self.process = None
            #                else:
            #                    return
            """>>> e
            <Event 1L mins=set(['0']) hours=AllMatch([]) days=AllMatch([]) months=AllMatch([
            ]) label='Hourly Test' plugin='PluginDemo' client='scranton_hermes' map=1L legen
            d=2L params='these are params'>
            >>> conf = Util.load_client_conf(client=e.client)
            >>> conf
            {'scranton_hermes': {'acalogapikey': 'c91dff2e46824d3ee7b04ae9d7a75af3f60b407d',
            'curriculoggmserver': 'localhost', 'plugin': 'PluginDemo', 'curriculogclient':
            'jreeser', 'acalogapiurl': 'http://apis.jreeser.dev.aws.acalog.com', 'plugin_fil
            e': 'test', 'curriculoggmport': '4735', 'dbname': 'hermes_scranton', 'curriculog
            gmurl': 'http://beta.curriculog.com/gearman/'}}
            >>> name = 'plugins.' + conf[e.client]['plugin_file']
            >>> name
            >>> fromlist = [name]
            >>> mod = __import__(name, globals(), locals(), fromlist, -1)
            >>> plugin = eval("mod.%s" % conf[e.client]['plugin'])
            """
            try:
                self.logging.info("check")
                self.logging.info("checking : %s" % self.client)
                client_conf = Util.load_client_conf(client=self.client)
                if self.pluginfile != None:
                    eventPluginFile = self.pluginfile
                else:
                    eventPluginFile = client_conf[self.client]['plugin_file']
                if self.plugin != None:
                    eventPlugin = self.plugin
                else:
                   eventPlugin = client_conf[self.client]['plugin']
                try:
                    if HermesCronServices:
                        service_handler = HermesCronServices(self.client, eventPlugin, eventPluginFile)
                except NameError:
                    from services.HermesCronServices import HermesCronServices
                    service_handler = HermesCronServices(self.client, eventPlugin, eventPluginFile)     
                service_handler.initClient(self.client, self.map, self.legend, self.params, debug=True)
                plugin = service_handler.plugin
                self.logging.info("params: %s" % (type(self.params)))
                #self.process._set_logging()
                self.process = plugin.Cron(client=self.client, map=self.map, legend=self.legend, params=self.params, event = None)
                self.lastrun = datetime.today()
                e.set(**{'lastrun' : self.lastrun})
            except Exception as e:
                self.logging.info("check failed : %s" % e)
                pass
            
    def __str__(self):
        return ("Event(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" %
                (self.id, self.mins, self.hours, self.days, self.months, self.label, self.plugin, self.pluginfile, self.client, self.map, self.legend, self.params))
        

class Cron(object):
    def __init__(self):
	from services.HermesCronServices import HermesCronServices as HermesServices
        Event._set_logging()
        self.events = Event.select()
        self.logger = logging.getLogger('hermes.cron')
    def _check(self):
	Event._set_logging()
        t1 = datetime(*datetime.now().timetuple()[:5])
        self.logger.info('Cron initiated, checking events for %s' % t1)
        for e in self.events:
            gevent.spawn(e.check, t1)
        t1 += timedelta(minutes=1)
        s1 = (t1 - datetime.now()).seconds + 1
        self.logger.info("Checking again in %s seconds" % s1)
        self.events = Event.select()
        job = gevent.spawn_later(s1, self._check)

    def run(self):
#        next_event = datetime(*datetime.now().timetuple()[:5])
#        while True:
#            for e in self.events:
#                e.check(next_event)
#
#            next_event += timedelta(minutes=1)
#            now = datetime.now()
#            while now < next_event:
#                dt = next_event - now
#                secs = dt.seconds + float(dt.microseconds) / 1000000
#                logging.debug("Sleeping from %s to %s (%s secs)" % (now, next_event, secs))
#                time.sleep(secs)
#                self.events = Event.select()
#                now = datetime.now()
        self._check()
        while True:
            gevent.sleep(60)


if __name__ == '__main__':
    main()
