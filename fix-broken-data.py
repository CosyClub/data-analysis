#!/usr/bin/env python
#
# The c++ data collection code contains 2 bugs that affects data collection
# This script attempts to reconstruct what the data actually should have
# been from what was recorded. Note this script should only be invoked once
# per csv - doing so again will further "fix" the data, and actually break it
#
##############################################################################
#
# The c++ data collection code contains this line:
#
# float delta = clock.beat_progress() < 0.5 ? since_beat : -until_beat;
#
# There are two issues with this:
#
# If beat_progress() > 0.5 then the delta is indeed -until_beat,
# but its until the NEXT beat, not the current beat, hence we
# should record the beat number as being get_beat_number() + 1
# This is not done. We can reconstruct the original data by simply
# adding 1 to any beat number where the delta is negative
#
# The second issue is that beat_progress() can sometimes go slightly over 1
# I /think/ this occurs when a single frame stradles the beat boundary,
# since we only call "passed_beat()" once per frame in main.cpp, where as
# beat_progress() increases continously over the whole frame, hence if we are
# a millisecond before the frame when passed_beat() is called we don't increment
# the beat, but then later in that 16ms frame when we call beat_progress() the
# value may be greater than 1 since we have passed into the next frame
# Unfortunetely this cannot be detected by looking at any individual line
# of data output by the client, but can be seen if the the recoreded
# delta ever decreases over a single beat - since the csv rows are recorded
# in order of keypresses, and we can never go backwards in time. Hence
# if we see a decrease in delta over a single beat, add 1 to the beat for
# all values within the same beat, after the delta decreased
# This could miss some cases, eg where user only presses a single button within
# a frame where the bug occured - but that should be a very rare case (since its
# already a very rare case that beat_progress() is greater than 1)
#
##############################################################################

import sys
import os
import csv

# Magic numbers with index of the column in csv containing specified data
COL_BEAT    = 0
COL_ON_BEAT = 1
COL_DELTA   = 2
COL_KEYCODE = 3

BPM         = 138.0
MAX_DELTA   = (60.0 / BPM) / 2.0

filepath = sys.argv[1]

###############################################################
# Load the file to be fixed
print("Loading data file '{:s}'".format(filepath))

fh   = open(filepath, 'rb')
csvdata  = csv.reader(fh)

data = []

rawrows = [row for row in csvdata]
rawrows = rawrows[1:] # chop off header row

for row in rawrows:
    if(len(row) == 4):
        data.append([int(float(row[COL_BEAT   ])),
                     int(float(row[COL_ON_BEAT])),
                     float    (row[COL_DELTA  ]),
                     int(float(row[COL_KEYCODE]))])

fh.close()
###############################################################



###############################################################
# First pass - fix first bug outline in this script's preamble
bad_beat = -1
for i in range(0, len(data)):
    # If the bug has happened then we've passed into the next beat
    # Set current beat as the bad_beat
    if data[i][COL_DELTA] < 0:
        bad_beat = data[i][COL_DELTA]

    # And then increment all rows seen from here on with the beat = bad_beat
    if data[i][COL_BEAT] == bad_beat:
        data[i][COL_BEAT] = data[i][COL_BEAT] + 1
###############################################################



###############################################################
# Second pass - fix second bug outlined in this scripts preamble
bad_beat = -1
for i in range(1, len(data)):
    # If the bug has happened set this beat as a bad beat
    if (data[i-1][COL_BEAT ] == data[i][COL_BEAT ] and
        data[i-1][COL_DELTA] >  data[i][COL_DELTA]):
        bad_beat = data[i][COL_BEAT]

    # If this is part of a bad_beat then increment the beat
    if data[i][COL_BEAT] == bad_beat:
        data[i][COL_BEAT] = data[i][COL_BEAT]+1
###############################################################



###############################################################
# Write the fixed data back out, overriting the original csv
print("Writing data to csv")
fh = open(filepath, 'wb')
writer = csv.writer(fh)
writer.writerow(['BeatNumber', 'OnBeat', 'BeatDiff', 'Key'])
for i in range(0, len(data)):
    writer.writerow(data[i])
fh.close()
###############################################################
