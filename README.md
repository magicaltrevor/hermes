hermes-digarc
=============

version of hermes for digarc

##Rough API Documentation:

###Modules:
- map = HermesMaps
- dataStore = DataStore
- legend = HermesLegend
- sources = HermesSources
- storeAttributes = StoreAttributes
- imported = DataStoreImported

###Get urls are as follows:
```
/api/client/module/method/{Jsonencoded string of params}
```

To start the api in dev mode go to the root hermes directory and type:
```
python api.py
```

###Examples:
####Getting a map
```
http://localhost:8008/api/cornell/map/getMap/{"mapId":3}
```

####Post urls
This is a work in progress for now "puts" can be performed via GET
Example:
```
http://localhost:8008/api/scranton_hermes/map/saveMap/{"externalTypeId":3, "mapName":"ApiTest", "legendFields":{"24": "Course Revisions:", "30": "Last Modified", "25": "Keywords:", "22": "Repeatable:", "26": "Last Updated:", "27": "Parent", "20": "Previously Listed as:", "21": "Notes:", "11": "Prerequisites:", "10": "Lecture Lab Hours:", "13": "Prerequisite Corequisites:", "12": "Concurrent Prerequisites:", "15": "Class Restrictions:", "14": "Corequisites:", "17": "Graduate Credit:", "16": "Major Restrictions:", "19": "Cross-listed with:", "18": "Equivalent Courses:", "23": "Terms offered", "28": "Is Active", "29": "Creation Date", "1": "Source", "3": "Course Oid", "2": "Catalog Id", "5": "Prefix", "4": "Course Type", "7": "Name", "6": "Code", "9": "Credit Hours:", "8": "Description"},"fileMapping":"['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '0', '27', '28', '29', '30']"}
```


##Hermes Maps
Maps external data sources to fields in digarc systems (tells hermes how to store data in the data store)
ex: Banner Monthly Update

###Properties 
-  Needs a version
-  Needs a name
-  Needs details
-  Has and belongs to many legends

###Returns
-  Return by digarc id (returns all maps for that catalog, latest version is implied)
-  Return by name (latest version is implied returns all maps with that name)
-  Return by has_legend (returns all maps that have a legend attached, assumes latest version)
-  Return by name, version, digarc_id (returns all maps that match name, version, and digarc_id)
-  Return by name, digarc_id (current version is implied)


##Hermes Legends
Used by maps as referencial information to map external data sources to fields in digarc systems

###Properties
- Needs a digarc id
- Needs details
- Has and belongs to a map


##DSL:
- A digarc property has a Hermes Legend
- A digarc property has a Hermes Map through a Hermes Legend
- A digarc property has many Hermes Map references
- A hermes map (can) belongs to many digarc objects
- A hermes legend has and belongs to a hermes map
- A hermes legend belongs to a digarc object through a hermes legend id
- A hermes data source has many maps
- A hermes map has and belongs to a hermes data source
- Cron (which is not a recorded object) has many Events
- Events have many Service actions




_See below for Testing_

![Hermes Stack Diagram](https://github.com/digarc/hermes-digarc/raw/master/hermes-stack.png)

##Testing:
Run the following commands in the python command line:
```
from engines import *
from testHermes import testHermes
r = testHermes()
r.setupFresh() # PASSED
r.listExternalSources() # PASSED
r.activateSource('banner') # PASSED
r.activateSource('curriculog') # PASSED
r.testDeleteMapsandLegends()   #  PASSED
r.testOutdatedMapsandLegends() # PASSED
r.testScopeLegends() # PASSED
r.testSavingLegend() # PASSED
r.testGetLegend() # PASSED
r.addBannerLogMap() # PASSED
```
or in the hermes-digarc/ directory, run : 
```
python testHermes.py
```

---

Start of new docs

---

-   Hermes Documentation
    -   About Hermes
    -   Hermes and Digital Architecture
        -   DataStore


Hermes Documentation
====================

About Hermes
------------

Hermes is an integration manager. To put it simply Hermes gives you the
tools to build a dynamic api for extracting data from one system to
provide a cached datastore to a dynamic api for exporting to another
system. It acts as a translator through a series of plugins and data
mapping / customizations to get data out of one system and into another
via an automated process.

Hermes and Digital Architecture
-------------------------------

There is a customized version of Hermes created for Digital Architecture
that is for integrating it’s line of products (Acalog and Curriculog)
with the client school’s SIS system (Banner, DataTel, Peoplesoft etc.)
This consists of Hermes core code which contains controls for both the
DataStore, the Map and Legend engines and the Services layer.

### DataStore

The data store is a key/value pair based storage system that stores the
data that has been extracted from the “export” system. For example if
you wanted to extract your email to import into some type of data mining
software the email system would be the “export” system and the
Datamining system would be the “import” system. In our example the data
would be extracted from the email system, using a map and the key /
values would be stored in the DataStore based on that map. All data is
extracted and flattened to a CSV like format and the map defines the key
for each field. So in our example an extracted email record might look
like this:

    sender@yahoo.com,recipient@gmail.com,2012-12-25 00:00:00TZ, Hello World, Hello there world this is the body of the email message.

Therefore a map might look like this:

    {"action": "modifify", "delimiter": "comma", "systemFieldNames": {"1": "sender", "2": "recipient", "3": "recieved_at", "4": "subject", "5": "body"}, "systemDefinitions": ["1", "2", "3", "4", "5"]}

The other fields are explained in more detail under Maps but for the
purposes of our example look at systemFieldNames, you’ll notice that
each label is assigned a number 1 for sender 2 for recipient etc. Then
in systemDefinitions it defines the order these appear in the extracted
and flattened data, which in this simple example is just 1,2,3,4,5 but
they can repeat. For example if the sender appeared at the end of the
data as well the systemDefinition would be 1,2,3,4,5,1.

A datastore object consists of three things. A datastore record which
tracks the type of data, the system it came from, the file it came from,
the map that it used for import the created at time the modified time
and the raw flattened data. The datastore\_attribute object is the
key/value pair object which has the field name, the field value, the
data type, it’s parent datastore id, created, modified, and delete
times. For example the data and map above would generate the following
datastore records:

    datastore_id: Parent_datastore_object_id
    field_name: sender
    field_value: sender@yahoo.com
    created_at: time_it_was_imported
    modified_at: NULL
    deleted_at: NULL

    datastore_id: Parent_ds_id
    field_name: recipient
    field_value: recipient@gmail.com
    created_at: time_it_was_imported
    modified_at: NULL
    deleted_at: NULL

And so on.
