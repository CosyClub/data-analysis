#!/usr/bin/env python

import sys
import os
import glob
import csv
import re
import matplotlib.pyplot as plt
import numpy             as np

# Magic numbers with index of the column in csv containing specified data
COL_BEAT    = 0
COL_ON_BEAT = 1
COL_DELTA   = 2
COL_KEYCODE = 3

BPM         = 138.0
MAX_DELTA   = (60.0 / BPM) / 2.0

OUT_DIR = os.path.abspath('outputs/') + "/"

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

#######################################################################
# Generate list of csv files to load from the input arguments
# Each is a path to directory containing csv files

if(len(sys.argv) <= 1):
    print("ERROR: Bad usage, please specify directories containg data to analyse")
    exit

# get absolute paths
dirs  = list(map   (lambda x: os.path.abspath(x),      sys.argv[1:]))

# get list of csv files in each directory
files = list(map   (lambda x: glob.glob(x + "/*.csv"), dirs        ))

# Flatten the list from 2d to 1d
files = [f for sublist in files for f in sublist]

file_dates = list(map((lambda x: re.search('(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})\.csv',
                                           os.path.basename(x)).group(1)),
                      files))
print(file_dates)
#######################################################################


#######################################################################
# Load data from files
def load_file(filepath):
    print("Loading data file '{:s}'".format(filepath))

    fh   = open(filepath, 'rb')
    csvdata  = csv.reader(fh)

    output = []


    rawrows = [row for row in csvdata]
    rawrows = rawrows[1:] # chop off header row

    for row in rawrows:
        if(len(row) == 4):
            output.append([int(float(row[COL_BEAT   ])),
                           int(float(row[COL_ON_BEAT])),
                           float    (row[COL_DELTA  ]),
                           int(float(row[COL_KEYCODE]))])

    fh.close()
    return output
data = list(map(load_file, files))
#######################################################################


def analyse_missed_beats(data):
    first_beat = data[0          ][COL_BEAT]
    last_beat  = data[len(data)-1][COL_BEAT]

    print("First beat: {:d}, last: {:d}".format(first_beat, last_beat))

    cur_run        = 0
    last_on_beat   = 1
    max_missed_run = 0
    min_missed_run = 0
    max_hit_run    = 0
    min_hit_run    = 0
    num_hit        = 0
    num_missed     = 0
    last_beat_seen = first_beat-1


    for row in data:
        print(row)

def analyse_beat_delta(name, data):
    print("Analysing beat delta for file: {:s}".format(name))

    deltas = np.zeros(len(data))

    for i in range(0, len(data)):
        deltas[i] = data[i][COL_DELTA]

    plt.figure()
    n, bins, patches = plt.hist(x=deltas, bins=31, range=(-MAX_DELTA, MAX_DELTA), normed=True)
    plt.title("Beat Delta for " + name)
    plt.xlabel("Beat Delta (seconds)")
    plt.ylabel("Count")
    plt.grid(True)

    for c, p in zip(bins, patches):
        if  (c > 0.150 or c < -0.150):
            plt.setp(p, 'facecolor', 'red')
        elif(c > 0.100 or c < -0.100):
            plt.setp(p, 'facecolor', 'yellow')
        else:
            plt.setp(p, 'facecolor', 'green')

    plt.savefig(OUT_DIR + "beat_delta_" + name + ".png")


full_data = []
for i in range(0, len(files)):
    full_data = full_data + data[i]

for i in range(0, len(files)):
    analyse_beat_delta(file_dates[i], data[i])

analyse_beat_delta("all", full_data)

#map(analyse_missed_beats, data)
