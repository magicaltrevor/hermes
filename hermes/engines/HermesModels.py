from hermes.engines.databases import *
from datetime import datetime, date
import time 
import simplejson
from pprint import pprint
import urllib
from sqlobject.sqlbuilder import *
from operator import itemgetter
import logging
import hermes.lib.util as Util
import sys
import re

def sortMultipleKeys(items, columns) :
    """
        This code is used to sort a list by multiple keys in the sub dicts
    """
    # The following code was based on http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys/1144405
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
    def comparer(left, right) :
        for fn, mult in comparers :
            result = cmp(fn(left), fn(right))
            if result :
                return mult * result
        else :
            return 0

    return sorted(items, cmp=comparer)

def selectSpecial(mainTableClass, joinExp, fields, whereExp, **kwargs):
    """This will construct special queries using sqlbuilder."""
    """mainTableClass expects main class to work from (usually the "FROM" in a sql query)"""
    """joinExp expects a SQLExpression join object"""
    """fields expects a list of SQLExpression fields you want returned ex: [Datastore.q.id, Datastore.q.map, SearchAttributes.q.fieldName]"""
    """whereExp expects a SQLExpression where clause"""
    """**kwargs expects any special operations you want to do see http://www.sqlobject.org/SQLBuilder.html#select ex: distinct=True or groupBy=SearchAttributes.q.fieldName"""
    """ selectSpecial(StoreAttributes, joinExp = LEFTJOINOn(StoreAttributes, DataStore, StoreAttributes.q.datastore == DataStore.q.id), fields = [StoreAttributes.q.fieldValue]
                      whereExp = AND(DataStore.q.dataType == 'record', StoreAttributes.q.fieldName == 'Prefix'), distinct=True)"""
    conn = mainTableClass._connection
    select = Select(fields, where=whereExp, join=joinExp, **kwargs)
    sql = conn.sqlrepr(select)
    rows = conn.queryAll(sql)
    if len(fields) < 2:
        formatted_rows = [rows[p][j] for p in range(len(rows)) for j in range(len(fields))]
        rows = formatted_rows
    return rows


class HermesLegend(SQLObject) :
    """
        Hermes Legend
        ==========================
        
        The Hermes Legend connects the system template to the hermes map
        
        
        +-------------------+                                 +----------------------+
        |  HermesMap        |                                 |  System Template     |
        |-------------------|                                 |----------------------|
        |                   |         +--------------+        |                      |
        |                   | <----+  |  Legend      | <----+ |                      |
        |                   | +---->  |              | +----> |                      |
        |                   |         +--------------+        |                      |
        +-------------------+                                 +----------------------+
    """
    
    class sqlmeta :
        table="hermes_legend"
    systemItemId = IntCol(length=11, default=None)
    modified = DateTimeCol(default=datetime.now())
    details = StringCol()
    current = BoolCol(default=True)
    systemType = ForeignKey('HermesSystems')
    
    # Joins
    # Each legend has one map
    maps = RelatedJoin('HermesMap', joinColumn='legend_id', otherColumn='map_id', intermediateTable='hermes_map_to_hermes_legend', createRelatedTable=True)
    
    def _set_client(self, value=None):
        self.client = value
    
    def _set_client_connection(self, value=None):
        self.client_connection = value
        
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.hermeslegend')
    
    """
    def _get_mapName(self) :
        ""
            Retrieve the Legend's Map's Name.
            
            ** returns map name **
        ""
        
        mapName = None
        
        if len(self.maps) > 0:
            return self.maps[0].name
        
        return mapName
    
    """
    
    def __repr__(self) :
        return "<HermesLegend('%i', '%s', '%s', '%s', '%s')>" % (self.id, self.systemItemId, self.details, self.current, self.systemType)
    
    @classmethod
    def saveLegend( self, legendFields, mapId=None, systemItemId=None, systemType=None, id=0) :
        """
            Save legend, find map of mapId, then add the legend to the map
            
            - id        : required
                   OR
            - Map id    : required
            - systemItemId : required
            
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        systemLegendId = 0
        
        # Map id and system id are required if the id was not passed
        if id < 1 and (mapId is None or systemItemId is None or systemType is None) :
            return systemLegendId
        
        legendDict = {
                    'details'    : simplejson.dumps(legendFields),
                    'current'    : True
                    }
        
        if id > 0 :
            systemLegend = HermesLegend.get(id)
            
            legendDict['modified'] = datetime.today()
            
            systemLegend.set(**legendDict)
            
            if mapId is None:
                mapId = systemLegend.maps[0].id
                
        else :
            """
                Search by mapId and systemItemId to ensure there is only one legend per map and systemItemId
            """
            existingLegends = list(HermesMap.get(mapId).importLegendSQL.filter(AND(
                                                                                HermesLegend.q.systemItemId == int(systemItemId),
                                                                                HermesLegend.q.systemType == int(systemType))))
            
            # if a legend matches by mapId, systemItemId, and systemType
            if len(existingLegends) > 0 :
                systemLegend = HermesLegend.get(existingLegends[0].id)

                legendDict['modified'] = datetime.today()
                
                existingLegends[0].set(**legendDict)
                
            else :
                legendDict['systemItemId'] = int(systemItemId)
                legendDict['systemType'] = int(systemType)
                
                # else add new legend
                systemLegend = HermesLegend(**legendDict)
            
        # Get New legends Id
        systemLegendId = systemLegend.id
        
        """
            Add legend to map if not associated
        """
        if mapId :
            legendMapIds = [ slmap.id for slmap in systemLegend.maps ]
            
            if int(mapId) not in legendMapIds :
                # Select Map
                legendMap = HermesMap.get(int(mapId))
                # Select Legend
                legend = HermesLegend.get(systemLegendId)
                # Add map to legend
                legend.addHermesMap(legendMap)
        
        
        return systemLegendId
    
    @classmethod
    def deleteLegend(self, id = None) :
        """
            Delete a Map Legend
            
            **Returns:**
            Bool: True/False
            
            **Usage:**
            Removes the connection of the Map to the system item 
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        if id and int(id) > 0:
            try:
                
                # remove map
                HermesLegend.delete(int(id))
                
                return True
            except:
                pass
            
        return False
    
    @classmethod
    def getLegend( self, id=None, systemItemId=None, systemType=None, mapId=None ):
        """
            Retrieve a Legend
            
            **Params:**
            - id    : required
            
            ** Optional Params if you don't have the legendId:**
            - systemItemId
            - systemType
            - mapId
            
            **Returns:**
            A Dict:
            - legend_id : the legend id
            - legend    : dict of the legend
            - fullname    : fullname of the map
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        print 'get legend  ( systemItemId : %s, mapId : %s, legendId : %s)' % (systemItemId, mapId, id)
        
        if id :
            """
                 If they passed in the legend id
            """
            legend = HermesLegend.get(int(id))
            
            map = legend.maps[0]
            
            dbLegend = simplejson.loads(legend.details, encoding='utf-8')
            
            return {
                    'legend_id' : int(legend.id),
                    'details' : dbLegend,
                    'name' : map.name,
                    'current' : legend.current,
                    'hermes_system'   : {
                                            'id'    : legend.systemType.id,
                                            'short' : legend.systemType.shortName,
                                            'name'  : legend.systemType.name,
                                            'status': legend.systemType.status
                                           }
                    }
        
        elif systemItemId and systemType and mapId:
            """
                 If they passed in the map id, grab legend by that map id and system id
            """
            map = HermesMap.get(int(mapId))
        
            for legend in map.importLegendSQL.filter(AND(
                                                        HermesLegend.q.systemItemId == int(systemItemId),
                                                        HermesLegend.q.systemType == int(systemType)
                                                        )):
                        
                dbLegend = simplejson.loads(legend.details, encoding='utf-8')
                
                return {
                        'legend_id' : int(legend.id),
                        'details' : dbLegend,
                        'name' : map.name,
                        'current' : legend.current,
                        'hermes_system'   : {
                                                'id'    : legend.systemType.id,
                                                'short' : legend.systemType.shortName,
                                                'name'  : legend.systemType.name,
                                                'status': legend.systemType.status
                                               }
                        }
                
        return False
    
    @classmethod
    def getScopedLegends( self, systemItemId=None, mapSystem=None, systemType=None, outdated=None, includeMaps=False, mapType=None ):
        """
            Select the Legends
            
            **Optional Params: **
                You may pass in the following parameters:
                * systemItemId    : int 
                * mapSystem       : the system that the map is connected to
                * systemType      : system short name or id that the legend points to
                * outdated    : Boolean
            
            ** Returns: **
            
            { <SYSTEM SHORT NAME>: [{'current': bool,
                                          'system_id': int,
                                          'id': <LEGEND ID>,
                                          'name': <MAP NAME>,
                                          'map_id': <MAP ID>,
                                          'system_id': <SYSTEM ID>,
                                          'system_name': <SYSTEM NAME>}]
            
            Example:
            [{'banner': [{'current': False,
                          'system_id': 11,
                          'id': 3,
                          'name': 'Banner Monthly Test Outdated',
                          'map_id': 4,
                          'system_id': 3,
                          'system_name': 'Banner'}]

            
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        print 'get legend  ( systemItemId : %s, system : %s , outdated : %s )' % (systemItemId, systemType, outdated)
        
        #legends = []
        legends = {}
        
        query = OR(
                   HermesSystems.q.status == 'active',
                   HermesSystems.q.status == 'locked',
                   )
        
        if mapSystem :
            try :
                query = AND(
                        query,
                        HermesSystems.q.id == int(mapSystem)
                        )
            except:
                query = AND(
                        query,
                        HermesSystems.q.shortName == mapSystem
                        )
        
        # Loop systems, ordered by name
        for system in HermesSystems.select(query).orderBy(['name']) :
            
            filterMap = AND(
                            HermesMap.q.status == 'active',
                            HermesMap.q.current == True
                            )
            
            if mapType :
                # catch incase they do not pass valid string as mapType
                try:
                    filterMap = AND(
                            filterMap,
                            HermesMap.q.type == mapType.lower()
                            )
                except:
                    pass
            
            # loop over each system children maps, ordered by name
            for map in system.childrenMaps.filter(filterMap).orderBy(['name']) :
                
                noLegends = True
                
                filterQuery = None
                if systemItemId :
                    try:
                        # Filter the legends by the system id if passed to function
                        filterQuery = HermesLegend.q.systemItemId == int(systemItemId)
                    except:
                        pass
                
                if systemType :
                    if filterQuery :
                        filterQuery = AND(
                                        filterQuery,
                                        HermesLegend.q.systemType == int(systemType)
                                        )
                    else :
                        filterQuery = HermesLegend.q.systemType == int(systemType)
                
                # loop over each system's map's legends
                for legend in map.importLegendSQL.filter(filterQuery) :
                    if outdated and (outdated == True or outdated == "1" or outdated == "true") and legend.current :
                        break
                    
                    """
                    safeToAdd = True
                    
                    
                    # check if older version exists
                    
                    if system.shortName in legends:
                        for mapDict in legends[system.shortName]:
                            self.logging.info("legend system: %s" % (legend.systemItemId))
                            if map.name == mapDict.get('name') and legend.systemItemId == mapDict.get('system_item_id') :
                                safeToAdd = False
                    
                    # If the legend has not been added
                    
                    if safeToAdd :
                    """
                    
                    if system.shortName not in legends:
                        legends[system.shortName] = []
                    
                    legends[system.shortName].append({
                                                       'id'           : int(legend.id),
                                                       'name'         : map.name,
                                                       'system_id'    : int(system.id),
                                                       'system_name'  : system.name,
                                                       'system_item_id'    : int(legend.systemItemId),
                                                       'map_id'       : int(map.id),
                                                       'current'      : legend.current,
                                                       'type'         : map.type
                                                       })
                    noLegends = False
                        
                """
                    To display maps that have not been assigned a legend
                """
                if includeMaps and systemItemId and noLegends:
                    """
                    safeToAdd = True
                    if system.shortName in legends:
                        for mapDict in legends[system.shortName]:
                            if map.name == mapDict.get('name') and int(systemItemId) == mapDict.get('system_item_id') :
                                safeToAdd = False
                    
                    
                        If the legend has not been added
                    
                    if safeToAdd :
                    """
                    if system.shortName not in legends:
                        legends[system.shortName] = []
                        
                    legends[system.shortName].append({
                                                           'id'            : 0,
                                                           'name'          : map.name,
                                                           'system_id'     : int(system.id),
                                                           'system_name'   : system.name,
                                                           'system_item_id': int(systemItemId),
                                                           'map_id'        : int(map.id),
                                                           'current'       : False,
                                                           'type'         : map.type
                                                           })
        
        return legends
   
    
class HermesMap(SQLObject) :
    """
        Hermes Map
        ==========================
        
        Each map has 1 system, but may have multiple legends, and multiple dataStoreItems.
        
          +--------------+
          |   System     |                                           +----------------+
          |--------------|                                           |    Legend      |
          |              |                                           |----------------|
          |              |     +-----------------+         +-------+ |                |
          +--------------+     |    Map          |         | +-----> |                |
               ^ +             |-----------------|         | |       +----------------+
               | |             |                 | <-------+ |
               | +---------->  |                 | +---------+
               +------------+  |                 | <-------+ |       +----------------+
                               +-----------------+         | |       |   Legend       |
                                     ^ +                   | |       |----------------|
                                     | |                   | +-----> |                |
                                     | |                   +-------+ |                |
                                     | |                             +----------------+
                                     | |
                                     | |        +--------------------+
                                     | |        |     DataStore      |
                                     | |        |--------------------|
                                     | |        |                    |
                                     | +------> |                    |
                                     +--------+ |                    |
                                                +--------------------+
        
    """
    
    class sqlmeta:
        table="hermes_map"

    name = StringCol(length=50, default=None)
    modified = DateTimeCol(default=datetime.now())
    details = StringCol()
    status = StringCol(length=20, default="active")
    type = StringCol(length=30, default="record")
    current = BoolCol(default=True)
    
    # Joins
    importLegend = RelatedJoin('HermesLegend', joinColumn='map_id', otherColumn='legend_id', intermediateTable='hermes_map_to_hermes_legend', createRelatedTable=True)
    importLegendSQL = SQLRelatedJoin('HermesLegend', joinColumn='map_id', otherColumn='legend_id', intermediateTable='hermes_map_to_hermes_legend', createRelatedTable=False)
    systemType = ForeignKey('HermesSystems')
    
    dataStoreItems = SQLMultipleJoin( 'DataStore', joinColumn='map' )
    
    
    def _set_client(self, value=None):
        self.client = value
    
    
    def _set_client_connection(self, value=None):
        self.client_connection = value
    
        
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.hermesmap')
    
    
    def __repr__(self):
        return "<HermesMap('%i','%s','%s','%s')" % (self.id, self.systemType.id, self.name, self.details)
    
    
    @classmethod
    def validateMap(self, system, name, systemFieldNames, systemDefinitions, id = 0, action='modify', status="active", details=None, mapType='record') :
        
        self._connection = self.client_connection['read']
        
        #try:
        client = None
        if hasattr(self, 'client'):
            client = self.client
        
        systemDict = HermesSystems.getSystems(filter = system, returnMeta=True)
        if len(systemDict) > 0:
            systemId = systemDict[0]['id']
            systemName = systemDict[0]['short']
        
            name = "%s.%s" % ('plugins', systemName)
            mod = __import__(name, globals(), locals(), [name], -1)
            #plugin = eval("mod.%s" % systemName.title())
            plugin = eval("mod.%s('%s')" % (systemName.title(), client))
            
            searchKeys = {
                        'prefix'         : None, 
                        'code'           : None, 
                        'name'           : None,
                        'id'             : None,
                        'system_item_id' : None,
                    }
            
            if hasattr(plugin, 'validateMap' ) :
                #plugin._set_logging()
                #plugin.__init__(client=client)
                
                return plugin.validateMap(system, name, systemFieldNames, systemDefinitions, searchKeys, id = 0, action='modify', status="active", details=None, mapType='record')
                
            else :
        
                zz = ['^%s$|: %s$' % (searchKey,searchKey) for searchKey in searchKeys.iterkeys()]
                
                # Check if attribute is "name" or ends with ": name"
                p = re.compile(r'%s' % '|'.join(zz), re.I)
                
                for a in systemFieldNames.iterkeys() :
                    x = p.search(a)
                    if x:
                        i = a[x.span()[0]: x.span()[1]].replace(': ', '').lower()
                        searchKeys[i] = x.string
                
                print "systemFieldNames"
                print systemFieldNames
                print "Search Keys"
                print searchKeys
                print "Search Key prefix"
                print searchKeys.get('prefix', None)
                
                """
                    Store the attributes dict in the raw data column, convert None to "", convert ints and floats to string
                """
                attributesDict = {}
                for key, value in systemFieldNames.iteritems():
                    #self.logging.info('attribute type: %s' % (type(value)))
                    
                    if value is None:
                        value = ""
                    
                    if type(value) is int or type(value) is float:
                        value = str(value)
                    
                    attributesDict[str(key.encode('utf-8'))] = value 
                
                if searchKeys.get('id', None) or searchKeys.get('system_item_id', None) :
                    """
                        Add if it has a Id or system_item_id attribute
                    """
                    fieldKey = None
                    
                    if searchKeys.get('system_item_id', None) :
                        
                        fieldKey = 'system_item_id'
                        
                    elif searchKeys.get('id', None) :
                        
                        fieldKey = searchKeys['id']
                        
                    
                    if fieldKey :
                        return True
                
                elif searchKeys.get('prefix', None) and searchKeys.get('code', None) and searchKeys.get('name', None) :
                    """
                        Add if it has a prefix / code / name
                    """
                    return True
                
                elif searchKeys.get('name', None) :
                    """
                        Add if it has a Name attribute
                    """
                    return True
                
                else:
                    self.logging.info("addItem but it failed man")
                    return False
        
    
    @classmethod
    def saveMap(self, system, name, systemFieldNames, systemDefinitions, id = 0, action='modify', status="active", details=None, mapType='record') :
        """
            Save a Hermes Map
            
            If a map of same name already exists, it will copy the legends of that map and mark them as current = False
            
            You may pass in the system shortName or the system id when you save a map.
        """
        # write Connection
        self._connection = self.client_connection['write']
        self._connection.expireAll()
        
        id = int(id)
        systemId = 0
        systemName = None

        systemDict = HermesSystems.getSystems(filter = system, returnMeta=True)
        if len(systemDict) > 0:
            systemId = systemDict[0]['id']
            systemName = systemDict[0]['short']
            systemDict = systemDict[0]
        else :
            return False
    
        mapType = mapType.lower()
        
        print systemDict['meta']
        
        # Set Connection to the same as this function
        HM = HermesMap
        HM._connection = self._connection
        
        print "id : ", id

        # if id passed edit that map
        if id > 0 :
            existingMap = HM.get(id)
        else :
            params = []
            # else grab by system
            params.append(HermesMap.q.systemType == systemId)
            
            # grab by name and system if a Multiple Map System
            if systemDict.get('meta', None) and systemDict['meta'].get('mms','0') == '1':
                
                params.append(HermesMap.q.name == name)
           
            # Filter by map type
            params.append(HermesMap.q.type == mapType)
            
            print self.logging
            
            self.logging.info("test logging")
            
            self.logging.info("%s" % HermesMap.select(AND(
                                            *params
                                            ), orderBy = ['-name']))
            print "select map from db that matches filter"
            print HermesMap.select(AND(
                                        *params
                                        ), orderBy = ['-name'])
            # grab latest map to copy templates to new map
            latestMaps = HermesMap.select(AND(
                                            *params
                                            ), orderBy = ['-name'])
            
            if latestMaps.count() > 0 :
                print "found latestMaps"
                if details and 'external-map-id' in details:
                    for latestMap in latestMaps:
                        latestMapDetails = simplejson.loads(latestMap.details, encoding='utf-8')
                        
                        if details['external-map-id'] == latestMapDetails['external-map-id'] :
                            print "found map by way of external-map-id" 
                            existingMap = latestMap
                            id = existingMap.id
                        
                else :
                    print "found map by way of grabbing first one"
                    existingMap = latestMaps[0]
                    id = existingMap.id
        
        """
            Create Dict for adding a new Map
        """
        print type(systemFieldNames), systemFieldNames
        if type(systemFieldNames) != dict:
            simplejson.loads(systemFieldNames)
        
        
        newTranslatorMapDetails = {
                            "delimiter" : "comma", 
                            "action" : action, 
                            "systemFieldNames" : systemFieldNames, #This defines the fieldnames of the columns, it may be used more than once, this is a lookup key.
                            "systemDefinitions" : systemDefinitions # This maps the column positions to a systemFieldName, the order represents the columns in the system 1:1 ratio
                            }
        
        if details is not None :
            newTranslatorMapDetails.update(details)
        
        newTranslatorMap = {
                            'systemType' : systemId,
                            'name'       : name,
                            'modified'   : datetime.now(),
                            'details'    : simplejson.dumps(newTranslatorMapDetails),
                            'type'       : mapType,
                            'current'    : True
                            }
        
        if status:
            # Catch that they must pass in active / inactive
            if status == 'active' or status is True:
                newTranslatorMap['status'] = 'active'
            else:
                newTranslatorMap['status'] = 'inactive'
        
        self.logging.info("map id: %s " % id)
        
        if id > 0 :
            print "id: ", id
            # if id passed, updated existing map
            existingMap.set(**newTranslatorMap)
            
            # update map's legends to not be current
            for legend in existingMap.importLegendSQL:
                """
                    Find better way to do this, must update connection to the write connection
                """
                legend._connection = self._connection
                legend.set(**{'current' : False})
            
            # remove all datastore items that belong to this map
            for datastore in existingMap.dataStoreItems:
                DataStore.deleteItem(datastore.id)
            
            newMap = existingMap
            
        else :
            # Add new map
            print "add new map"
            newMap = HermesMap(**newTranslatorMap)
        self.client_connection['read'].expireAll()
        return newMap.id
    
    @classmethod
    def getMap(self, id=None) :
        """
            Get a Specific Map Details, including the count of how many legends are pointing to that map (without timestamp)
            
            **Return a dict:**
                * id            : id of map
                * name          : name 
                * legend        : map's legend
                * map           : map's fileMap
                * system_type   : id of system type
                * action        : map's action - currently only 'modify'
                * has_legends   : count of the legends referencing this map name
        """
        
        # read Connection
        self._connection = self.client_connection['read']
        
        print "connection", self._connection
        
        if type(id) is dict:
            id = id.get('id', 0)
        
        if id and int(id) > 0:
            """
                If they passed in a map id > 0
            """
            map = HermesMap.get(int(id))
            
            print "mapDetails", map.details
            
            dbLegend = simplejson.loads(map.details, encoding='utf-8')
            
            print "dbLegend", dbLegend
            
            details = dbLegend.copy()
            
            del details['systemFieldNames']
            del details['systemDefinitions']
            del details['action']
            
            mapDict = {
                'id'                 : str(map.id),
                'name'               : map.name,
                'systemFieldNames'   : dbLegend['systemFieldNames'], 
                'systemDefinitions'  : dbLegend['systemDefinitions'],
                'system_type'        : map.systemType.id,
                'action'             : dbLegend['action'],
                'type'               : map.type,
                'has_legends'        : len(map.importLegend),
                'status'             : map.status,
                'current'            : map.current,
                'details'            : details
                }
            
            print "mapDict", mapDict
            
            return mapDict
        """
            If they didn't pass a map id or map name
        """
        return False
            
    @classmethod
    def getScopedMaps(self, active=True, shortName=None, meta=None, filter=None, groupBySystem=False):
        """
            Get a list of maps, ordered by system
            
            **Params**
            - active        :    bool
            - shortName     :    short name to only grab maps from that system
            - filter        :    allows you to pass a key/value pair to search the map
            - groupBySystem :    return the maps organized by the maps, includes a count of the amount of items available to map to 
            
            **Example of Filter Argument:**
                Plugin can pass filter={'external-map-id' : proposal['approvalProcessID']}  to find the map that connects to the external-map-id
            
            ** Returns: **
                List of Maps
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        scopedMaps = []
        
        query = OR(
                   HermesSystems.q.status == 'active',
                   HermesSystems.q.status == 'locked',
                   )
        
        if shortName :
            """
                If they passed in a shortName, then only return the maps that belong to that shortName
            """
            query = AND(
                       query,
                       HermesSystems.q.shortName == shortName)
        
        for system in HermesSystems.select(query, orderBy = HermesSystems.q.name) :
            
            systemMaps = []
            
            # loop the maps belonging to this system
            filterQuery = None
            print "Active passed for getScopedMaps: ", active
            if active:
                filterQuery = AND(
                                  HermesMap.q.status == 'active',
                                  HermesMap.q.current == True
                                  )
            
            for map in system.childrenMaps.filter(filterQuery).orderBy(['name', 'type']):
                
                """
                    filtering = True;  when you don't want to add the map
                    filtering = False; when you want to add the map
                """
                filtering = False
                #self.logging.info("filter: %s" % filter)
                
                print "filter", filter
                
                if filter is not None:
                    details = simplejson.loads(map.details)
                    
                    #self.logging.info("details: %s" % details)
                    
                    for key, value in filter.iteritems():
                        # if still filtering out the map
                        print "key", key
                        if not filtering :
                            # if the filter key is in the details and matches
                            if key in details :
                                print "found key", type(details[key])
                                print "search for ", value, type(value)
                                if type(details[key]) is str :
                                    if str(details[key]) != str(value):
                                        filtering = True
                                elif type(details[key]) is int :
                                    if details[key] != int(value):
                                        filtering = True
                            elif key == 'type':
                                if map.type != str(value):
                                    filtering = True



                #self.logging.info("filter: %s" % filtering)
                
                # if filtering is false / You want to add the map
                if not filtering :
                    mapDict = {
                               'name'       : map.name,
                               'id'         : map.id,
                               'system_id'  : int(system.id),
                               'status'     : map.status,
                               'current'    : map.current,
                               'type'       : map.type
                               }
                    
                    if groupBySystem :
                        """
                            When grouping by system, return the meta data for each map
                        """
                        meta = simplejson.loads(map.details, encoding='utf-8')
                        
                        del meta['systemFieldNames']
                        del meta['systemDefinitions']
                        del meta['action']
                        
                        mapDict['meta'] = meta
                        
                    if meta :
                        fileSummary = {}
                        
                        mapDict['system_name'] = system.name
                        
                        """
                            Create summary of the file data for the datastore items connected to this map
                        """
                        for item in map.dataStoreItems.filter(None).orderBy('fileID'):
                            
                            if str(item.fileSystem.id) not in fileSummary:
                                fileSummary[str(item.fileSystem.id)] = {}
                            
                            if item.fileID not in fileSummary[str(item.fileSystem.id)] :
                                fileSummary[str(item.fileSystem.id)][str(item.fileID)] = datetime.strftime(item.createdAt, '%Y/%m/%d %H:%M:%S')
                                
                        mapDict['files'] = fileSummary
                    
                    # Add map dict to list of maps for this system
                    systemMaps.append(mapDict)
            
            
            if groupBySystem :
                """
                    Group By System and return System Details
                """
                
                availableSystemItems = []
                
                print system.meta
                
                if system.meta is not None:
                    meta = simplejson.loads(system.meta)
                    
                    print meta
                    
                    if meta.get('mms','0') == '1':
                        print "call to get listSystemItems"
                        # Get count of available system items if mms is enabled
                        availableSystemItems = HermesSystems.listSystemItems(system.shortName)
                
                
                systemDict = {
                                'short'             : system.shortName, 
                                'name'              : system.name,
                                'status'            : system.status,
                                'id'                : system.id,
                                'maps'              : systemMaps,
                                'system_item_count' : len(availableSystemItems)
                              }
                
                meta = system.meta
                
                if meta is not None:
                    meta = simplejson.loads(meta)
                
                systemDict['meta'] = meta
                
                scopedMaps.append(systemDict)
                
            else :
                """
                    Do not group the maps by system, return list of maps
                """
                scopedMaps.extend(systemMaps)
                
                
        return scopedMaps
   
    @classmethod
    def deleteMap(self, id=None):
        """
            When you delete a map, it will delete all children legends first
        """
        # write Connection
        self._connection = self.client_connection['write']

        if id and int(id) > 0:
            try:
                map = HermesMap.get(int(id))
                
                for legend in map.importLegend:
                    HermesLegend.delete(legend.id)
                
                for datastore in map.dataStoreItems:
                     DataStore.deleteItem(datastore.id)
                
                HermesMap.delete(int(id))
                
                return True
            except:
                pass
            
        return False   
   
   
class HermesSystems(SQLObject):
    """
        Hermes Systems
        ==========================
        
        - Active Directory
		- MySQL
		- PostgreSQL
		- MSSQL
    """
    
    class sqlmeta:
        table="hermes_systems"
    shortName = StringCol(length=20, default=None)
    name = StringCol(length=20, default=None)
    meta = StringCol(default=None)
    modified = DateTimeCol(default=datetime.now())
    status = StringCol(length=20, default='inactive') # active / inactive / locked
    
    # Joins
    childrenMaps = SQLMultipleJoin( 'HermesMap', joinColumn='system_type' )

    def __repr__(self):
        return "<HermesSystems('%i, %s','%s','%s')" % (self.id, self.shortName, self.name, self.meta)
    
    def _set_client(self, value=None):
        self.client = value
    
    def _set_client_connection(self, value=None):
        self.client_connection = value
    
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.hermessystems')
        
    @classmethod
    def addDefaultSystems(self):
        """
            Will add the following records to the table:
            
            +----+-----------------+------------------+------+---------------------+----------+
            | id | short_name      | name             | meta | modified            | status   |
            +----+-----------------+------------------+------+---------------------+----------+
            |  1 | activeDirectory | Active Directory | NULL | 2012-10-08 11:06:16 | inactive |
            |  2 | mySQL           | MySQL            | NULL | 2012-10-08 11:06:16 | inactive |
            |  3 | postgre         | PostgreSQL       | NULL | 2012-10-08 11:06:16 | inactive |
            |  4 | MSSQL           | MSSQL            | NULL | 2012-10-08 11:06:16 | inactive |
            +----+-----------------+------------------+------+---------------------+----------+
        """
        systemsDefault = [
                                {'shortName' : 'activeDirectory',
                                    'name' : 'Active Directory'},
                                {'shortName' : 'mySQL',
                                    'name' : 'MySQL'},
                                {'shortName' : 'postgre',
                                    'name' : 'PostgreSQL'},
                                {'shortName' : 'MSSQL',
                                    'name' : 'MSSQL'}
                                ]
        
        for system in systemsDefault:
            self.saveSystem(system)
        
        return True
       
    @classmethod
    def addNewSystem(self, systemDict={}):
        """
            Will add new system to available systems.
            
            The dict must contain the shortName and name keys.
            
            This is to be used by the api incase we want to add a new system later on
        """
        
        if 'shortName' in systemDict and 'name' in systemDict:
            return self.saveSystem(systemDict)
        
        return False
    
    @classmethod
    def deleteSystem(self, id=None):
        # write Connection
        self._connection = self.client_connection['write']
        
        if id and int(id) > 0:
            try:
                system = HermesSystems.get(int(id))
                
                if len(list(system.childrenMaps)) < 1:
                     system.status = "inactive"
                     return True
                
            except:
                pass
            
        return False    
    
    @classmethod
    def getSystems(self, active=True, returnMeta=False, filter=None):
        """
            Return a dict of systems
            
            if active is false, return the status of each system
            
            if returnMeta = True : return the meta in the dictionary of systems
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        systems = [];
        
        query = None
        if active:
            query = OR(
                       HermesSystems.q.status == 'active',
                       HermesSystems.q.status == 'locked',
                       )
        
        if filter:
            if type(filter) is int:
                systemRecord = HermesSystems.get(filter)
                
                intSystemDict = {
                                'id'    : systemRecord.id,
                                'short' : systemRecord.shortName,
                                'name'  : systemRecord.name,
                                'status': systemRecord.status
                               }
                
                if returnMeta :
                    meta = systemRecord.meta
                    
                    if meta is not None:
                        meta = simplejson.loads(meta)
                    
                    intSystemDict['meta'] = meta
                
                intSystemDict = [intSystemDict]
                
                print intSystemDict
                
                return intSystemDict
                
            elif type(filter) is str or type(filter) is unicode:
                # if they pass in the systemTypeId as the short name convert to id
                query = HermesSystems.q.shortName == filter
        
        
        for system in list(HermesSystems.select(query, orderBy = ['name'])):
            systemDict = {
                        'id'     : system.id, 
                        'short'  : system.shortName, 
                        'name'   : system.name,
                        'status' : system.status
                      }
            
            if returnMeta :
                meta = system.meta
                
                if meta is not None:
                    meta = simplejson.loads(meta)
                
                systemDict['meta'] = meta
            
            if active is not True:
                systemDict['status'] = system.status
             
            systems.append(systemDict)
             
        return systems
    
    @classmethod
    def listSystemItems(self, system, id=None, itemType='record', template=False, client=None):
        
        if client == None:
            if hasattr(self, 'client'):
                client = self.client
        
        data = []
        
        if client :
            self.logging.info("Retrieve Data for System: %s" % system)
            
            # Get the system settings
            systemDict = HermesSystems.getSystems(filter = system, returnMeta=True )
            
            if len(systemDict) > 0:
                systemDict = systemDict[0]
            
            if systemDict.get('meta', None) and systemDict['meta'].get('dmh','0') == '1':
                
                #try:
                    
                name = "hermes.%s.%s" % ('plugins', system)
                mod = __import__(name, globals(), locals(), [name], -1)
                #plugin = eval("mod.%s" % system.title())
                print "init the plugin"
                #plugin = eval("mod.%s('%s', %s, %s, %s)" % (system.title(), client, None, None, None))
                plugin = eval("mod.%s('%s')" % (system.title(), client))
                #plugin._set_logging()
                #plugin.__init__(client=client)
                
                data = plugin.listSystemItems(id, itemType, template)
                """        
                except Exception as e:
                    e = sys.exc_info()  
                    self.logging.info("listSystemItems : %s" % e[0])
                    self.logging.info("%s" % e[1])
                    return data
                """
            else :
                
                self.logging.info("%s does not have the Dynamic Map Helper (dmh) setting enabled" % client)
                
        return data
      
    @classmethod
    def saveSystem(self, system):
        """
             Save / Update an System
             
             **Params:**
             Dictionary of key/value for system settings.
             
             **You must pass in the shortName**
             
             'status'    : default 'inactive', may pass 'active'
             
         """
        # write Connection
        self._connection = self.client_connection['write']
        
        if 'shortName' in system :
             newSystem = {
                        'shortName' : system['shortName']
                        }
             
             if 'name' in system:
                 newSystem['name'] = system['name']
                 
             if 'status' in system:
                  # Catch that they must pass in active / inactive
                  if system['status'] == 'locked' :
                      newSystem['status'] = 'locked'
                  elif system['status'] == 'active' or system['status'] is True:
                      newSystem['status'] = 'active'
                  else:
                    newSystem['status'] = 'inactive'
                  
             # Check if exist in database
             existingSystem = HermesSystems.select(HermesSystems.q.shortName == system['shortName'])
            
             if existingSystem.count() > 0 :
                 # set modified date to today
                 newSystem['modified'] = datetime.today()
                 
                 existingSystem[0].set(**newSystem)
                
             else :
                 HermesSystems(**newSystem)
             
             # if they passed settings, and it is a dict 
             if 'meta' in system and type(system['meta']) is dict:
                 return self.saveSystemSettings({system['shortName'] : system['meta'] }) 
             
             return True
             
        return False
    
    @classmethod
    def saveSystemSettings(self, settings=None):
        """
            Pass a dict with keys as the short names and the values as a dict of settings
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        success = 0
        
        if settings:
            
            for system, systemSettings in settings.iteritems():
                
                if 'url' in systemSettings:
                    
                    # URL should start with "http://"
                    url = systemSettings['url']
                    if url[0:7] != 'http://':
                        url = 'http://' + url
        
                    # Add slash to end of url
                    if url[-1:] != '/':
                        url += '/'
                    
                    systemSettings['url'] = urllib.quote_plus(url)
                
                existingSystem = HermesSystems.select(HermesSystems.q.shortName == system)
                
                if existingSystem.count() > 0 :
                    existingSystem[0].set(**{'meta' : simplejson.dumps(systemSettings), 'modified': datetime.today()})
                    
                    success += 1
        
            if success >= len(settings) :
                return True
            else :
                return False
    
class DataStore(SQLObject):
    """
        DataStore
        
        +--------------+
        |   Map        |
        |--------------|
        |              |
        |              |                                        +----------------------+
        |              |                                        |     StoreAttributes  |
        +--------------+                                        |----------------------|
                ^ +          +------------------+               |                      |
                | |          |    DataStore     |        +----->|                      |
                | |          |------------------|        | +---+|                      |
                | +--------> |                  |        | |    +----------------------+
                +----------+ |                  | +------+ |
                             |                  | <--------+
                             +------------------+
                                         ^ +                    +----------------------+
                                         | |                    |   DataStoreImported  |
                                         | |                    |----------------------|
                                         | +----------------->  |                      |
                                         +-------------------+  |                      |
                                                                +----------------------+
        
    """
    
    class sqlmeta:
        table="hermes_datastore"
    fileID = IntCol(length=11, notNone=False, default=0)
    fileSystem = ForeignKey('HermesSystems')
    dataType = StringCol(length=255, default='')
    map = ForeignKey('HermesMap')
    # do not store since majority will be cron job
    #createdBy = IntCol(length=11, notNone=False, default=0)
    createdAt = DateTimeCol(default=datetime.now())
    modifiedAt = DateTimeCol(default=datetime.now())
    deletedAt = DateTimeCol(default=None)
    
    # This system column is not needed
    #system = StringCol(length=255, default='')
    rawData = BLOBCol(length=16777215,default=None)  # Medium Blob
    
    children = RelatedJoin('DataStore', joinColumn='from_id', otherColumn='to_id',
                           intermediateTable='hermes_datastore_relationships')
    parents = RelatedJoin('DataStore', joinColumn='to_id', otherColumn='from_id',
                          intermediateTable='hermes_datastore_relationships', createRelatedTable=False)
    store_attributes = MultipleJoin('StoreAttributes', joinColumn='datastore_id') #joinColumn=?
    
    _scoped_store_attributes = SQLMultipleJoin('StoreAttributes', joinColumn='datastore_id') #joinColumn?
    
    SQLimported = SQLMultipleJoin('DataStoreImported', joinColumn='datastore_id')
    
    def _set_client(self, value=None):
        self.client = value
    
    def _set_client_connection(self, value=None):
        self.client_connection = value
        
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.datastore')
    
    @classmethod
    def _set_search_cache(self):
        self.found = {
                     'record' : {}
                     }
        self.missing = {
                         'record' : {}
                         } 
        
    @classmethod
    def addItem(self, datastoreDict, attributes ):
        """
        
            Add new if not exist or update
        
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        datastoreId = 0
        datastoreItem = []
        self.logging.info(" ")
        self.logging.info(" ")
        self.logging.info("addItem")
        """
            begin of new way
        """
        
        params = []
        joins = []
        
        params.append(DataStore.q.map == datastoreDict['mapID'])
        params.append(DataStore.q.dataType == datastoreDict['dataType'])
        
        """
        This block of commented out code is replaced by the regex following it
        searchKeys = []
        for a in map(lambda l: l.lower(), attributes.iterkeys()) :
            if a.find(': ') > -1 :
                searchKeys.append(a.split(': ')[-1])
            else :
                searchKeys.append(a)
        """
        
        """
            Search the attributes and pull out the searchKeys which are used to ensure that the items doesn't exist.
            
            It will search for if the attribute is "name" or ends with ": name"
        """
        searchKeys = {
                        'prefix'         : None, 
                        'code'           : None, 
                        'name'           : None,
                        'id'             : None,
                        'system_item_id' : None,
                    }
        
        zz = ['^%s$|: %s$' % (searchKey,searchKey) for searchKey in searchKeys.iterkeys()]
        
        # Check if attribute is "name" or ends with ": name"
        p = re.compile(r'%s' % '|'.join(zz), re.I)
        
        for a in attributes.iterkeys() :
            x = p.search(a)
            if x:
                i = a[x.span()[0]: x.span()[1]].replace(': ', '').lower()
                searchKeys[i] = x.string
        
        print "Attributes"
        print attributes
        print "Search Keys"
        print searchKeys
        
        """
            Store the attributes dict in the raw data column, convert None to "", convert ints and floats to string
        """
        attributesDict = {}
        for key, value in attributes.iteritems():
            #self.logging.info('attribute type: %s' % (type(value)))
            
            if value is None:
                value = ""
            
            if type(value) is int or type(value) is float:
                value = str(value)
            
            attributesDict[str(key.encode('utf-8'))] = value 
        
        if searchKeys.get('id', None) or searchKeys.get('system_item_id', None) :
            """
                Add if it has a Id or system_item_id attribute
            """
            print "Had id or system_item_id"
            fieldKey = None
            
            if searchKeys.get('system_item_id', None) :
                
                fieldKey = 'system_item_id'
                
            elif searchKeys.get('id', None) :
                
                fieldKey = searchKeys['id']
                
            
            self.logging.info("adding item id, key : %s" % fieldKey)
            
            daId = Alias(StoreAttributes, "daId")
            daIdQuery = daId.q.datastore == DataStore.q.id

            daIdQuery = AND(
                        daIdQuery,
                        daId.q.fieldName == fieldKey)
        
            params.append(daId.q.fieldValue == str(attributesDict[fieldKey]))
        
            joins.append( LEFTJOINOn(None, daId, daIdQuery))
        
        elif searchKeys.get('prefix', None) and searchKeys.get('code', None) and searchKeys.get('name', None) :
            """
                Add if it has a prefix / code / name
            """
            print "adding item prefix / code / name"
            self.logging.info("adding item prefix / code / name")
            
            daPrefix = Alias(StoreAttributes, "daPrefix")
            daCode = Alias(StoreAttributes, "daCode")
            daName = Alias(StoreAttributes, "daName")
            
            """
                Join the Prefix
            """
            daPrefixQuery = daPrefix.q.datastore == DataStore.q.id 
        
            daPrefixQuery = AND(
                        daPrefixQuery,
                        daPrefix.q.fieldName == searchKeys['prefix'])
        
            params.append(daPrefix.q.fieldValue == attributesDict[searchKeys['prefix']])
        
            joins.append( LEFTJOINOn(None, daPrefix, daPrefixQuery))
            
            """
                Join the Code
            """
            daCodeQuery = daCode.q.datastore == DataStore.q.id
        
            daCodeQuery = AND(
                        daCodeQuery,
                        daCode.q.fieldName == searchKeys['code'])
        
            params.append(daCode.q.fieldValue == attributesDict[searchKeys['code']])
        
            joins.append( LEFTJOINOn(None, daCode, daCodeQuery))
            
            """
                Join the Name
            """
            daNameQuery = daName.q.datastore == DataStore.q.id
        
            daNameQuery = AND(
                        daNameQuery,
                        daName.q.fieldName == searchKeys['name'])
        
            params.append(daName.q.fieldValue == attributesDict[searchKeys['name']])
            
            joins.append( LEFTJOINOn(None, daName, daNameQuery))
        
        elif searchKeys.get('name', None) :
            """
                Add if it has a Name attribute
            """
            print "adding item name"
            self.logging.info("adding item name")
            daName = Alias(StoreAttributes, "daName")
        
            # Join the Name
            daNameQuery = daName.q.datastore == DataStore.q.id
            
            daNameQuery = AND(
                        daNameQuery,
                        daName.q.fieldName == searchKeys['name'])
        
            params.append(daName.q.fieldValue == attributesDict[searchKeys['name']])
            
            joins.append( LEFTJOINOn(None, daName, daNameQuery))
        
        else:
            self.logging.info("addItem but it failed man")
            return False
        
        
        print "check if item exists"
        print DataStore.select(AND(
                                    *params
                                    ),join=joins).distinct()
        
        
        datastoreItem = list(DataStore.select(AND(
                                                *params
                                                ),join=joins).distinct())
                
        datastoreDict['rawData'] = simplejson.dumps(attributesDict, encoding='utf-8')
        
        print datastoreItem
        print datastoreDict
        
        if datastoreItem != []:
            # Update record
            print "update record"

            datastoreDict['modifiedAt'] = datetime.today()

            datastoreId = datastoreItem[0].id

            datastoreItem[0].set(**datastoreDict)

        else:
            # Create a new record
            print "create record"
            datastoreId = int(DataStore(**datastoreDict).id)
        
        #self.logging.info("datastoreId: %s" % datastoreId)
        print "datastoreId ********"
        print datastoreId
        # Add items attributes
        if len(attributesDict) > 0 and datastoreId and datastoreId > 0:
            StoreAttributes.addAttributes(datastoreId, attributesDict)
        
        print "datastoreId ********"
        print datastoreId
        
        return datastoreId
    
    @classmethod
    def deleteItem(self, dataStoreId):
        """
            Delete Attributes, Data from the datastore imported too
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        try:
            """
            # when the ForeignKey Cascade setting is set to true, you no longer need to loop over items attributes and imported records
            item = DataStore.get(dataStoreId)
            
            for attribute in item.store_attributes:
                StoreAttributes.delete(attribute.id)
            
            for imported in item.SQLimported:
                DataStoreImported.delete(imported.id)
            """
            
            #DataStoreImported.deleteMany(where = DataStoreImported.q.datastoreID == datastoreId )
            
            DataStore.delete(dataStoreId)
            
            return True
        except:
            return False
    
    
    @classmethod
    def getItem(self, id=None, showMeta=True, systemItemId=None, systemType=None, matchId=None):
        """
            Get the Datastore Item, including the attributes
            
            If the systemItemId, systemType are passed, search for matches of items
            If the matchId is passed, grab item and compare
            
            **Result**
            A dict containing the datastore item, plus all the attributes
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        item = {}
        
        if id :
            
            #try :
            datastoreRecord = DataStore.get(int(id))
            
            # Add custom attributes for item
            item.update( dict( ( attribute.fieldName, attribute.fieldValue ) for attribute in datastoreRecord.store_attributes ) )
            
            item['hermes_id'] = datastoreRecord.id
            item['hermes_type'] = datastoreRecord.dataType
            
            if showMeta :
                item['hermes_meta'] = {
                                'hermes_created'  : datastoreRecord.createdAt.isoformat(' '),
                                'hermes_modified' : datastoreRecord.modifiedAt.isoformat(' '),
                                'hermes_deleted'  : None,
                                'hermes_map'      : datastoreRecord.map.id,
                                'hermes_system'   : {
                                                        'id'    : datastoreRecord.map.systemType.id,
                                                        'short' : datastoreRecord.map.systemType.shortName,
                                                        'name'  : datastoreRecord.map.systemType.name,
                                                        'status': datastoreRecord.map.systemType.status
                                                       }
                                }
                
                if datastoreRecord.deletedAt is not None:
                    item['hermes_meta']['hermes_deleted'] = datastoreRecord.deletedAt.isoformat(' ')
                    
                """
                    if legendId and systemId are passed in, then create hermes_match attribute
                """
                if systemType and systemItemId and hasattr(self, 'client') :
                    client = self.client
                    
                    if client :
                        
                        # set the variables used in this search function
                        self._set_search_cache()
                        
                        system = HermesSystems.get(systemType)
                        
                        DestinationReport = None

                        name = "hermes.%s.%s" % ('plugins', system.shortName)
                        mod = __import__(name, globals(), locals(), [name], -1)
                        DestinationReport = eval("mod.%s('%s',%s,%s,%s)" % (system.shortName.title(), client, None, None, None))                        
            """
                Recursively add children
            """
            if len(datastoreRecord.children) > 0 :
                
                #self.logging.info("datastoreRecord.children : %s" % ([child.id for child in datastoreRecord.children]))
                
                childItems = [child.id for child in datastoreRecord.children]
                
                if len(childItems) > 0 :
                    item['children'] = []
                    for childItem in childItems:
                        item['children'].append(self.getItem(childItem, False))
            """
            except:
                return { 
                        "status" : "Error",
                        "message" : ["An error has occurred"] }
            """

        return item
    
    @classmethod
    def addFileData(self, mapId, data, fileID=0, fileSystem=None, dataType="record"):
        """
            Accept the file as a json object through the api, loop over each row and add the row as a datastore item according to mapId
            
            Parse each row as a systemItem and process according to the HermesMap
            
            ** Params: **
            - mapId    : the id of the map to add to datastore
            - data     : the contents of the file
            - fileID   : this is optional 
            - dataType : for the data type, default is record
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        if mapId and int(mapId) > 0 :
            map = HermesMap.getMap(int(mapId))
            
            #system = HermesSystems.get(map['system_type'])
            #'system'   : system.shortName,
            datastoreDict = {
                'dataType' : dataType,
                'mapID'    : int(mapId),
                'fileID'   : int(fileID)
            }
            
            if fileSystem:
                 datastoreDict['fileSystem'] = int(fileSystem)
                
            self.logging.info("datadict : %s" % (datastoreDict))
            
            # process data through map
            report = []
            for record in data:
                dataRecord = {}
                if len(record) >= len(map['systemDefinitions']):
                    for key, value in enumerate(map['systemDefinitions']):
                        if value != '0':
                            dataRecord[map['systemFieldNames'][value].encode('utf-8')] = record[key]
                            
                report.append(dataRecord)
            
            # loop over processed data and add items
            for key, attributes in enumerate(report):
                #self.logging.info("attributes 22: %s" % (attributes))
                datastoreId = self.addItem(datastoreDict, attributes)
                
            return True
            
        return False
    
    @classmethod
    def getDatastoreFields(self, searchParameters, systemFieldIds={}, systemType=None):
        """
            This function should be used to get fields from the datastore
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        results = {}
        
        if 'map_id' in searchParameters and 'system_id' in searchParameters and ('Prefix' in systemFieldIds or 'Code' in systemFieldIds or 'Name' in systemFieldIds):
            # Grab the legend for the map and system id
            legend = HermesLegend.getLegend( mapId=searchParameters['map_id'], systemItemId=searchParameters['system_id'], systemType=systemType )
            
            if searchParameters['map_id'] is None or int(searchParameters['map_id']) < 1 :
                return False
            
            map = HermesMap.getMap(id=searchParameters['map_id'])
            
            newSystemFieldIds = dict( (systemFieldKey, systemFieldValue) for systemFieldKey, systemFieldValue in systemFieldIds.iteritems() if systemFieldIds[systemFieldKey] in legend["details"] )
            
            kwargs = { "distinct" : True }
            
            for systemFieldKey, systemFieldValue in newSystemFieldIds.iteritems() :
                
                joinExp = LEFTJOINOn(StoreAttributes, DataStore, StoreAttributes.q.datastore == DataStore.q.id)
                
                fields = [StoreAttributes.q.fieldName, StoreAttributes.q.fieldValue]
                
                whereExp = AND(
                               DataStore.q.dataType == map['type'],
                               DataStore.q.map == searchParameters['map_id'],
                               StoreAttributes.q.fieldName == legend['details'][str(systemFieldValue)]
                               )
                
                resultTuple = selectSpecial(StoreAttributes, joinExp, fields, whereExp, **kwargs)
                values = [resultTuple[p][1] for p in range(len(resultTuple))]
                
                results[legend['details'][str(systemFieldValue)]] = values
                
        return results
        
    
    
    @classmethod
    def searchDatastore(self, searchParameters, displayTitleFields={}, systemType=None, order=None, showMatch=False, client=None):
        """
            
            
            **Parameters**
            @searchParameters
                        Example:
                        searchParameters = {
                                    'map_id' : 7
                                    'system_id' : 11
                                    }
                        
                        *** Pass Filters ***
                        #seaarchParameters['filter'] = [
                                                        {"Map Field Name goes here" : "value it equals goes here"}
                                                        ]
                        Only pass what you want to search. 
                        If you pass 'code' = '', it will search where code = ''
                        
                        searchParameters['paginate'] = {
                                    'start' : 0
                                    'end' : 25
                                    }
                        
                        #searchParameters['include_imported'] = True
                        
                        ***When searching by date with a Start and End***
                        #searchParameters["modified"] = [{"compare" : ">=", "value" : "2012/08/26" },{"compare" : "<=","value" : "2012/09/20"}]
                        ***When searching by date with only a End Date***
                        #searchParameters["modified"] = {"compare":"<=","value":"2012/09/19"}
                        ***When searching by date with only a Start Date***
                        #searchParameters["modified"] = {"compare":">=","value":"2012/08/27"}
                        
            @displayTitleFields
                        optional if the plugin has the "displayTitleFields" function defined
                        Example:
                            displayTitleFields={ 'Prefix' : '627', 'Code' : '629', 'Name' : '631' }
                            
            @order        Specifies the ordering of results, pass in the string name of a map field name or a list of strings of map field names
                            
            @showMatch    default: False
                        if set to true, will find a match in current system software to see if already exists
            
            @systemType
                        **Required
                        This is the system id that the legend is going into
                        system -> map -> legend -> systemType
                        
            **Returns:**
                a sorted list of the search results
        
        """
        # write Connection
        self._connection = self.client_connection['read']
        
        if client == None:
            if hasattr(self, 'client'):
                client = self.client
        
        
        if 'type' in searchParameters :
            searchType = searchParameters['type']
        else:
            searchType = 'record'
        
        results = []
        params = []
        joins = []
        
        kwargs = { "distinct" : True }
        
        aliases = {}
        aliasQuery = []
        
        searchSummary = {
                         "total"   : 0,
                         "results" : []
                         }
        
        self.logging.info("searchParameters %s" % searchParameters)
        
        if 'map_id' in searchParameters and 'system_id' in searchParameters:
            
            # Grab the Map, Legend, System
            map = HermesMap.getMap(id=searchParameters['map_id'])
            legend = HermesLegend.getLegend( mapId=searchParameters['map_id'], systemItemId=searchParameters['system_id'], systemType=systemType )
            system = HermesSystems.get(legend['hermes_system']['id'])
            
            name = "hermes.%s.%s" % ('plugins', system.shortName)
            mod = __import__(name, globals(), locals(), [name], -1)
            
            #pluginParams = {
            #                'specialParam' : searchParameters['system_id']
            #               }
            pluginParams = None
            plugin = eval("mod.%s('%s',%s,%s,%s)" % (system.shortName.title(), client, map, legend, pluginParams))
            
            """
                Setup the Joins and Conditions
            """
            params.append(DataStore.q.map == map['id'])
            params.append(DataStore.q.dataType == searchType)
            
            if 'include_imported' in searchParameters and searchParameters['include_imported']:
                params.append(DataStoreImported.q.importedAt == None)
            
            if 'modified' in searchParameters :
                value = searchParameters['modified']
                
                try :
                    try :
                        if value['compare']:
                            """
                                 If they passed in 1 date
                            """
                            filterDate = datetime.strptime(value['value'], '%Y/%m/%d')
                            
                            if value['compare'] == '>=':
                                """
                                    They passed in the start Date
                                """
                                params.append(func.date(DataStore.q.modifiedAt) >= filterDate.date())
                            elif value['compare'] == '<=':
                                """
                                    They passed in the end Date
                                """
                                params.append(func.date(DataStore.q.modifiedAt) <= filterDate.date())
                        
                    except:
                        """
                            If they passed in a start and end date
                        """
                        startMonth = datetime.strptime(value[0]['value'], '%Y/%m/%d')                    
                        endMonth = datetime.strptime(value[1]['value'], '%Y/%m/%d')                
                        params.append(func.date(DataStore.q.modifiedAt) >= startMonth.date())
                        params.append(func.date(DataStore.q.modifiedAt) <= endMonth.date())
                        pass
                    
                except :
                    pass
            
            # Datastore Imported
            joins.append( LEFTJOINOn(DataStore, DataStoreImported, AND(DataStore.q.id == DataStoreImported.q.datastore, DataStoreImported.q.systemItemId == int(searchParameters['system_id']) )))
            
            
            if 'filter' in searchParameters:
                
                for filterKey, filter in enumerate(searchParameters['filter']):
                    
                    print "search for : ", filter
                    fieldName = filter.keys()[0]
                    
                    # only use the alphabetical characters in the keyName
                    keyName = ''.join(e for e in fieldName if e.isalpha())
                    
                    if len(keyName) < 0 :
                        filterKey += 1
                        keyName = "filter%s" % filterKey
                    
                    aliases[keyName] = Alias(StoreAttributes, keyName)
                    
                    params.append(aliases[keyName].q.fieldValue == filter[fieldName])
                    
                    joins.append( LEFTJOINOn(None, aliases[keyName], AND(
                                                                        aliases[keyName].q.datastore == DataStore.q.id,
                                                                        aliases[keyName].q.fieldName == fieldName)))
            
            """ 
                Sort by Map Field Name 
            """
            if order is not None :
                
                if type(order) is not list :
                    order = [order]
                    
                print "order by for : ", order
                
                kwargs["orderBy"] = []
                
                for orderKey, orderField in enumerate(order):
                    
                    keyName = "OrderColumn%s" % orderKey
                    
                    aliases[keyName] = Alias(StoreAttributes, keyName)
                    
                    joins.append( LEFTJOINOn(None, aliases[keyName], AND(
                                                                        aliases[keyName].q.datastore == DataStore.q.id,
                                                                        aliases[keyName].q.fieldName == orderField)))
                
                    kwargs["orderBy"].append(aliases[keyName].q.fieldValue)
                
                                                          
            print "***************************************"
            print "***************************************"
            print "***************************************"
            
            
            joinExp = joins
            
            fields = [DataStore.q.id]
            
            whereExp = AND(
                            *params
                            )
            
            # find total of results
            resultTuple = selectSpecial(DataStore, joinExp, fields, whereExp, **kwargs)
            
            # return the total result
            searchSummary["total"] = len(resultTuple)
            
            # if a dict is passed in the searchParameters['paginate'] then add to the kwargs
            if 'paginate' in searchParameters and type(searchParameters['paginate']) is dict : 
                
                kwargs.update( searchParameters['paginate'] )
                
                # if pagination passed then reset the resultTuple variable with the paginated results
                resultTuple = selectSpecial(DataStore, joinExp, fields, whereExp, **kwargs)
            
            # convert the resultTuple to a list of ints
            values = [int(value) for value in resultTuple]
            print "values", values
            
            if hasattr(plugin, 'displayTitleFields' ) :
                
                print "call function to displayTitleFields"
                displayTitleFields = plugin.displayTitleFields(id=searchParameters['system_id'], itemType=searchType, legend=legend)
                
            self.logging.info("legend details: %s" % legend['details'])
            self.logging.info("displayTitleFields: %s" % displayTitleFields)
            
            # Loop over results and build list
            self.logging.info("Loop over results and build list")
            
            for id in values :
                
                datastoreRecord = DataStore.get(id)
             
                self.logging.info("datastore id : %s " % datastoreRecord.id)
                
                # dict containing the title fields
                fields = {}
                
                attributes = dict( ( attribute.fieldName, attribute.fieldValue ) for attribute in datastoreRecord._scoped_store_attributes )
                
                # format the title of the item in the plugin
                if len(displayTitleFields) > 0 :
                    
                    for key, field in displayTitleFields.iteritems() :
                        
                        if field in attributes :
                            fields[key.lower()] = attributes[field]
                    
                    
                # A Dict for each item
                item = {
                        'id'               : datastoreRecord.id,
                        'modified'         : datetime.strftime(datastoreRecord.modifiedAt, '%Y/%m/%d'),
                        'imported'         : None,
                        'requirements_met' : True
                        }
                
                # Get the imported Date
                for imported in datastoreRecord.SQLimported.filter(DataStoreImported.q.systemItemId == int(searchParameters['system_id'])):
                    item['imported'] = datetime.strftime(imported.importedAt, '%Y/%m/%d')
                
                # add the fields dict to the item dict
                item.update(fields)
                
                if showMatch and len(fields) > 0 and hasattr(plugin, 'searchResultSupplementalInformation' ):
                    
                    item.update( plugin.searchResultSupplementalInformation(fields=fields, datastoreRecord=datastoreRecord, attributes=attributes) )
                    
                results.append(item)
        
        searchSummary["results"] = results
        
        # return the summary of the search
        return searchSummary
        
    
    @classmethod
    def findChildrenMatchesToDatastore(self, report, dataStoreId, itemChildren=[], searchFields, legend=None ) : 
        """
            Loop over the children of a datastore item and search to see if there is a match in the destination system
			searchFields is a list of fields to search
        """
        
        results = {}
        
        if type(dataStoreId) is int :
            dataStoreItem = DataStore.get(dataStoreId)
       
            elif dataStoreItem.dataType == 'record' :
                print "findChildrenMatchesToDatastore"
                # Check if fields match
                results = report.findMatchRequirements(dataStoreItem, legend)
                
            # Loop datastore children
            for child in dataStoreItem.children :
                
                # only search records
                if child.dataType == "record" :
                    
                    # if already found, grab from self variable
                    if str(child.id) in self.found :
                        
                        results['found'][child.dataType][str(child.id)] = self.found[str(child.id)]
                    
                    # if already found, grab from self variable        
                    elif str(child.id) in self.missing :
                        
                        results['missing'][child.dataType][str(child.id)] = self.missing[str(child.id)]
                    
                    # if not found, then make api call
                    else :
                        
                        # Build Fields from select columns
                        fields = dict( ( attributes.fieldName.lower(), attributes.fieldValue ) for attributes in child.store_attributes if attributes.fieldName.lower() in searchFields )                        
                        
                        matches = report.findMatchToDatastore(fields)
                        
                        if matches != False and len(matches) > 0:
                            
                            results['found'][child.dataType][str(child.id)] = matches.keys()[0]
                            self.found[child.dataType][str(child.id)] = results['found'][child.dataType][str(child.id)]
                            
                        else :
                            
                            print results
                            print child.dataType
                            print child.id
                            
                            results['missing'][child.dataType][str(child.id)] = fields
                            self.missing[child.dataType][str(child.id)] = results['missing'][child.dataType][str(child.id)]
                                    
                if len(child.children) > 0 :
                    
                    childrenResults = self.findChildrenMatchesToDatastore(report, child.id, itemChildren)
                    
                    # Dynamically update the results
                    for key, value in results.iteritems():
                        if key in childrenResults :
                            for key2, value2 in results[key].iteritems(): # found
                                if key2 in childrenResults[key] : # type
                                    results[key][key2].update(childrenResults[key][key2])
                                else :
                                    results[key][key2] = childrenResults[key][key2]
                    
                    
        return results

    
class StoreAttributes(SQLObject):
    """
        Store Attributes
        
        Contains the attributes of the Datastore Item
    """
    
    class sqlmeta:
        table="hermes_datastore_attributes"
    datastore = ForeignKey('DataStore', cascade=True)
    fieldName = StringCol(length=255, default='')
    fieldValue = StringCol(default=None)
    dataType = StringCol(length=255, default='')
    createdAt = DateTimeCol(default=datetime.now())
    modifiedAt = DateTimeCol(default=datetime.now())
    deletedAt = DateTimeCol(default=None)
    
    
    def _set_client(self, value=None):
        self.client = value

    def _set_client_connection(self, value=None):
        self.client_connection = value
    
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.storeattributes')
    
    @classmethod
    def addAttributes(self, datastoreId, attributes, *itemType):
        """
            Once an item has been added to the datastore, you can addAttributes
            
            ** Params: **
            - datastoreId   : 
            - attributes    : dict of the attributes of item
            - type          : type of 
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        print "Add Attributes"
        
        # Grab the datastore record
        datastoreRecord = DataStore.get(datastoreId)
        
        # convert the rawData into a dict
        try :
            rawData = simplejson.loads(datastoreRecord.rawData.replace("'",'"'), encoding='utf-8')
        except:
            rawData = simplejson.loads(datastoreRecord.rawData, encoding='utf-8')
        
        # update the rawData with the new attributes
        rawData.update(attributes)
        rawData = simplejson.dumps(rawData, encoding='utf-8')
        
        # update the record
        datastoreRecord.set(rawData=rawData)
        
        # flag to know if the item was actually updated
        updated = False
        
        for key, value in attributes.iteritems():
            
            attributeDict = {
                'datastoreID' : datastoreId,
                'fieldName' : key,
                'fieldValue' : value
            }
            
            itemType = ''.join(itemType)

            if itemType != '':
                attributeDict['data_type'] = str(itemType)
            
            datastoreItemAttribute = list(datastoreRecord._scoped_store_attributes.filter(StoreAttributes.q.fieldName == attributeDict['fieldName']))
            
            """
            datastoreItemAttribute = list(StoreAttributes.select(AND(
                StoreAttributes.q.datastoreID == attributeDict['datastoreID'],
                StoreAttributes.q.fieldName == attributeDict['fieldName']
            )))
            """
            
            # if record exists
            if datastoreItemAttribute != []:

                # if value is different, update
                if datastoreItemAttribute[0].fieldValue != attributeDict['fieldValue'] :

                    attributeDict['modifiedAt'] = datetime.today()

                    # Update record
                    datastoreItemAttribute[0].set(**attributeDict)
                    
                    updated = True

            else:
                # Create a new record
                StoreAttributes(
                    **attributeDict
                )
                
                updated = True
        
        # remove the flag that this item was imported
        if updated :
            DataStoreImported.clearFlag(datastoreId)
        
        
        return True
    
    @classmethod
    def getAttributes(self, datastoreId):
        """
            retrieve a dict of the attributes of a datastore item
        """
        # read Connection
        self._connection = self.client_connection['read']
        
        datastoreItemAttributes = list(StoreAttributes.select(
                                                            StoreAttributes.q.datastoreID == datastoreId
                                        ))
        #,  StoreAttributes.q.fieldName != 'Approval Process Name'
        
        # if records exist
        if datastoreItemAttributes != []:

            fields = {}

            for attribute in datastoreItemAttributes :

                fields[attribute.fieldName] = attribute.field_value

            return fields

        return []

class DataStoreImported(SQLObject):
    """
        DataStoreImported
        
        Contains a lookup table if the datastore item has been imported
    """
    
    class sqlmeta:
        table="hermes_datastore_imported"
    datastore = ForeignKey('DataStore', cascade=True)
    systemItemId = IntCol(length=11, notNone=True)
    system = ForeignKey('HermesSystems')
    importedAt = DateTimeCol(default=datetime.now())
    
    def _set_client(self, value=None):
        self.client = value
    
    def _set_client_connection(self, value=None):
        self.client_connection = value
        
    @classmethod
    def _set_logging(self):
        self.logging = logging.getLogger('hermes.datastoreimported')
        
    @classmethod
    def markImported(self, datastoreId, systemItemId, system=None):
        """
            markImported
            
            Marks the item as imported into a system item or updates the imported date
            
            **Params:**
            @systemItemId    : this is the system id
            @system      : this is the system short name
        """
        # write Connection
        self._connection = self.client_connection['write']
        
        # Verify that they pass in 
        if system is None :
            return False
        else:
            systemDict = HermesSystems.getSystems(filter = system)
            
            if len(systemDict) > 0:
                system = systemDict[0]['id']
            else :
                system = 0
        
        importedItem = DataStoreImported.select(AND(
                                    DataStoreImported.q.datastore == int(datastoreId),
                                    DataStoreImported.q.systemItemId == int(systemItemId),
                                    DataStoreImported.q.system == int(system)))
        if importedItem.count() > 0 :
            importedItem[0].set(**{'importedAt' : datetime.today()})
            
            return importedItem[0].id

        else:
            # Create a new record
            datastoreImportedRecord = {
                                    'datastoreID' : int(datastoreId),
                                    'systemItemId' : int(systemItemId),
                                    'system' : int(system)
                                    }
            return int(DataStoreImported(**datastoreImportedRecord).id)
            
        return False

       
    @classmethod  
    def isImported(self, datastoreId, systemItemId, system=None):
        # read Connection
        self._connection = self.client_connection['read']
        
        if system is None :
            return False
        
        importedItem = DataStoreImported.select(AND(
                                    DataStoreImported.q.datastore == datastoreId,
                                    DataStoreImported.q.systemItemId == systemItemId,
                                    DataStoreImported.q.system == system))
        if importedItem.count() > 0 :
            return True
            #importedItem[0].set(**{'importedAt' : datetime.today()})
            #return importedItem[0].importedAt
        else:
            return False
    
    
    @classmethod
    def clearFlag(self, datastoreId):
        # write Connection
        self._connection = self.client_connection['write']
        
        DataStoreImported.deleteMany(where = DataStoreImported.q.datastoreID == datastoreId ) 
        
