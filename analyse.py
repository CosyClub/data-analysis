#!/usr/bin/env python

import sys
import os
import glob
import csv

#######################################################################
# Generate list of csv files to load from the input arguments
# Each is a path to directory containing csv files

# get absolute paths
dirs  = list(map   (lambda x: os.path.abspath(x),      sys.argv[1:]))

# get list of csv files in each directory
files = list(map   (lambda x: glob.glob(x + "/*.csv"), dirs        ))

# Flatten the list from 2d to 1d
files = [f for sublist in files for f in sublist]
#######################################################################

def load_file(filepath):
    print("Loading data file '{:s}'".format(filepath))

    fh   = open(filepath, 'rb')
    csvdata  = csv.reader(fh)

    output = []

    for row in csvdata:
        if(len(row) > 0):
            output.append(row)

    fh.close()
    return output[1:] # chop off header row

data = list(map(load_file, files))

print(data)
