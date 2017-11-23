#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 10:49:03 2017

@author: helger1
"""
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import schema

OSM_PATH = "seattle_washington.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


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

#CSV files
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema


NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def audit_street_type(street_types, street_name):
    """
       collects the last words in the "street_name" strings, if they are not
       within the expected list, then stores them
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def is_street_name(elem):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    """
        returns me a dictionary that match the above function conditions
    """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):
    """takes an old name to mapping dictionary, and update to a new one"""
    
    m = street_type_re.search(name)
    if m:
        for a in mapping:
            if a == m.group():
                name = re.sub(street_type_re, mapping[a], name)
    
    return name

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {} 
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        for i in NODE_FIELDS:
            if element.get(i):
                node_attribs[i] = element.attrib[i]
        for tag in element.iter("tag"):  
            problem = PROBLEMCHARS.search(tag.attrib['k'])
            if not problem:
                node_tag = {} 
                node_tag['id'] = element.attrib['id'] 
                node_tag['value'] = tag.attrib['v']  

                match = LOWER_COLON.search(tag.attrib['k'])
                if not match:
                    node_tag['type'] = 'regular'
                    node_tag['key'] = tag.attrib['k']
                else:
                    bef_colon = re.findall('^(.+):', tag.attrib['k'])
                    aft_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])
                    node_tag['type'] = bef_colon[0]
                    node_tag['key'] = aft_colon[0]
                    if node_tag['type'] == "addr" and node_tag['key'] == "street":
                        # update street name
                        node_tag['value'] = update_name(tag.attrib['v'], mapping) 
            tags.append(node_tag)
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for i in WAY_FIELDS:
            way_attribs[i] = element.attrib[i]
        for tag in element.iter("tag"):
            problem = PROBLEMCHARS.search(tag.attrib['k'])
            if not problem:
                way_tag = {}
                way_tag['id'] = element.attrib['id'] 
                way_tag['value'] = tag.attrib['v']
                match = LOWER_COLON.search(tag.attrib['k'])
                if not match:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = tag.attrib['k']
                else:
                    bef_colon = re.findall('^(.+?):+[a-z]', tag.attrib['k'])
                    aft_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])

                    way_tag['type'] = bef_colon[0]
                    way_tag['key'] = aft_colon[0]
                    if way_tag['type'] == "addr" and way_tag['key'] == "street":
                        way_tag['value'] = update_name(tag.attrib['v'], mapping) 

            tags.append(way_tag)
        position = 0
        for tag in element.iter("nd"):  
            nd = {}
            nd['id'] = element.attrib['id'] 
            nd['node_id'] = tag.attrib['ref'] 
            nd['position'] = position  
            position += 1
            
            way_nodes.append(nd)
    
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



### Helper Functions ###
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


### Main Function ###
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()



        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=False)