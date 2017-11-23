#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 10:50:04 2017

@author: helger1
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "seattle_washington.osm"
regex = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "North", "Northeast", "South", "Northwest", "Southwest","Southeast", "West",
            "East", "Way", "Loop", "Highway", "SW", "NW", "S", "N", "E", "W", "SE", "NE", "Terrace", "Crescent", "Circle",
            "Broadway"]

mapping = {"St": "Street",
           "Rd": "Road",
           "west": "West",
           "street": "Street",
           "st": "Street",
           "southeast": "Southeast",
           "nw": "NW",
           "boulevard": "Boulevard",
           "ave": "Avenue",
           "WY": "Way",
           "Ter": "Terrace",
           "St.": "Street",
           "Se": "SE",
           "SW,": "SW",
           "ST": "Street",
           "S.E.": "SE",
           "S.": "S",
           "Rd.": "Road",
           "RD": "Road",
           "Pl": "Place",
           "Pkwy": "Parkway",
           "PL": "Place",
           "N.": "N",
           "MainStreet": "Main Street",
           "Hwy": "Highway",
           "Dr": "Drive",
           "Dr.": "Drive",
           "Ct": "Court",
           "CT": "Court",
           "Blvd.": "Boulevard",
           "Blvd": "Boulevard",
           "Av.": "Avenue",
           "Ave": "Avenue",
           "Ave.": "Avenue",
           "AVE": "Avenue"
            }

# Search string for the regex. If it is matched and not in the expected list then add this as a key to the set.
def audit_street(street_types, street_name): 
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem): # Check if it is a street name
    return (elem.attrib['k'] == "addr:street")

def audit(): # return the list that satify the above two functions
    osm_file = open(OSMFILE, "r")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street(street_types, tag.attrib['v'])

    return street_types

#pprint.pprint(dict(audit())) # print the existing names

def string_case(s): # change string into titleCase except for UpperCase
    if s.isupper():
        return s
    else:
        return s.title()

# return the updated names
def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    
    name = ' '.join(name)
   

    return name

update_street = audit()

# print the updated names
for street_type, ways in update_street.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print name, "=>", better_name