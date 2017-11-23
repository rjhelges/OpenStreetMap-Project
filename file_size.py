#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 13:23:41 2017

@author: helger1
"""

import os
print('seattle_washington.osm: {} MB'.format(os.path.getsize('seattle_washington.osm')/1.0e6))
print('project.db: {} MB'.format(os.path.getsize('seattle.db')/1.0e6))
print('nodes.csv: {} MB'.format(os.path.getsize('nodes.csv')/1.0e6))
print('nodes_tags.csv: {} MB'.format(os.path.getsize('nodes.csv')/1.0e6))
print('ways.csv: {} MB'.format(os.path.getsize('ways.csv')/1.0e6))
print('ways_tags.csv: {} MB'.format(os.path.getsize('ways_tags.csv')/1.0e6))
print('ways_nodes.csv: {} MB'.format(os.path.getsize('ways_nodes.csv')/1.0e6)) # Convert from bytes to MB