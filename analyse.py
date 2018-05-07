#!/usr/bin/env python

import sys
import os
import glob
import csv
import re
import matplotlib
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


matplotlib.rcParams.update({'font.size': 16})

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

def analyse_beat_delta_hist(name, data):
    print("Analysing beat delta hist for: {:s}".format(name))

    deltas = np.zeros(len(data))

    for i in range(0, len(data)):
        deltas[i] = data[i][COL_DELTA]

    plt.figure(tight_layout=True)
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

    plt.savefig(OUT_DIR + name + "_beat_delta_hist.png")
    plt.close()

def analyse_beat_delta(name, data):
    print("Analysing beat delta for: {:s}".format(name))

    deltas       = [] # The first delta time per beat
    beats        = [] # x axis values corresponding to deltas array

    extra_deltas = [] # Extra delta times per beat (IE: where user pressed key more than once)
    extra_beats  = [] # x axis values corresponding to the extra_deltas array

    last_beat = -1

    for i in range(0, len(data)):
        new_beat  = data[i][COL_BEAT]
        new_delta = data[i][COL_DELTA]

        if new_beat == last_beat:
            # Then this is another key on a single beat
            extra_beats.append(new_beat)
            extra_deltas.append(new_delta)
        else:
            # then we have a new beat
            beats.append(new_beat  )
            deltas.append(new_delta)

        last_beat = new_beat

    fig, ax = plt.subplots(tight_layout=True)
    plt.title("Beat delta over time for " + name)
    plt.xlabel("Beat")
    plt.ylabel("Key Press Beat Delta")
    plt.grid(True)
    plt.ylim([-MAX_DELTA, MAX_DELTA])
    ax.plot(beats,       deltas,       linestyle='none', marker='o', color='green')
    ax.plot(extra_beats, extra_deltas, linestyle='none', marker='o', color='red')
    ax.axhspan( 0.100,  0.150,     alpha=0.5, color='yellow')
    ax.axhspan( 0.150,  MAX_DELTA, alpha=0.5, color='red')
    ax.axhspan(-0.100, -0.150,     alpha=0.5, color='yellow')
    ax.axhspan(-0.150, -MAX_DELTA, alpha=0.5, color='red')
    plt.savefig(OUT_DIR + name + "_beat_delta.png")
    plt.close()


full_data = []
for i in range(0, len(files)):
    full_data = full_data + data[i]

for i in range(0, len(files)):
    analyse_beat_delta_hist(file_dates[i], data[i])
analyse_beat_delta_hist("all", full_data)

for i in range(0, len(files)):
    analyse_beat_delta(file_dates[i], data[i])
