#!/usr/bin/python

import urllib, urllib2
from lxml import etree
from pprint import pprint
from datetime import datetime
import csv
import sys
import math

class ReportGenerator():

    def getReport(self, data, filemap, template):
        #pprint(data)
        report = []
        # return list of dicts
        for record in data:
            dataRecord = {}
            if len(record) >= len(filemap):
                for key, value in enumerate(filemap):
                    if value != '0':
                        dataRecord[template[value].encode('utf-8')] = record[key]
                        
            report.append(dataRecord)
            
        return report