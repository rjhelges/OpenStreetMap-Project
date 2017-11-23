#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 10:52:07 2017

@author: helger1
"""

import xml.etree.cElementTree as ET
import pprint


OSMFILE = "seattle_washington.osm"

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
    
pprint.pprint(count_tags(OSMFILE))