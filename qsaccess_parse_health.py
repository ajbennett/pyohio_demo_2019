#!/usr/bin/env python3

"""

qsaccess_parse_health.py

HealthKit -> QS Access -> Dropbox -> (...)

"""

import csv
import datetime
import os
import sys
import zipfile

import log
import requests

import pandas as pd
import numpy as np

lg = log.create_logger()
#
# ------------------------------------------------------------
#
# get most current file from Dropbox via API
#

# run in current directory
wdir = os.getcwd()
os.chdir(wdir)

get_new_file = True
csv_output_file = None
if get_new_file:
    # lazy ... put file in current directory
    wdir = os.getcwd()
    os.chdir(wdir)
    lg.info("downloading data from dropbox")
    # @TODO: factor out hardcoded file endpoint into config file
    db_url = "https://www.dropbox.com/s/rfamnrymmpbycnx/QS%20Health%20Data.csv?dl=1"
    csv_output_file = "QS Health Data.csv"
    try:
        r = requests.get(db_url)
        rdata = r.content
        txtdata = "".join(chr(x) for x in rdata)
        lg.info("got rdata from %s" % db_url)
        lg.info(type(rdata))
        lg.info(type(txtdata))
        # write file to disk
        fh = open(csv_output_file, 'w')
        lg.info("opened output file")
        fh.write(txtdata)
        lg.info("wrote output file")
        fh.close()
        lg.info("closed output file")
    except Exception as e:
        lg.info("encountered exception in file download: %s" % e)
        lg.info("using cached file")

#
# tidy the data a bit and get into the basic format that I want: date
# column (date) and weight column (float)
#

# ingest csv file
cfh = open(csv_output_file)
csvr = csv.reader(cfh, dialect='excel')
csvdata = [row for row in csvr]

#
# define column keys for dictionary
#
dkeys = csvdata[0]
cdata = []
for r in csvdata[1:]:
    cdata.append(dict(list(zip(dkeys, r))))

# construct a smaller data set (just use the main column)
#
# Note: These column names are the values established by the QS Access
# app on the iPhone
#
sdata = [(p["Start"], p["Weight (lb)"]) for p in cdata]
print(sdata)

#
# basic date string->date conversion function
#
# '21-Feb-2019 00:00'
def str_to_date(s):
    return datetime.datetime.strptime(s, "%d-%b-%Y %H:%M").date()

#
# process string dates into datetime objects
#
ndata = map(lambda p: (str_to_date(p[0]), p[1]), sdata)
print(ndata)

#
# strip out data before start date
# 
START_DATE = datetime.date(2019, 2, 14)
odata = [p for p in ndata if p[0] > START_DATE]
print(odata)

#
# write out to file and read from that into DataFrame using built-in
# CSV tools
#
# make the column names better and simpler
#
pdata = [('date', 'weight')]
pdata.extend(odata)
print(pdata)

cfh = open('fdata.csv', 'w')
cw = csv.writer(cfh, dialect='excel')
for row in pdata:
    cw.writerow(row)
cfh.close()

#
# demo: process the dataframes in various ways
#

#
# series v0
# 
# "raw" dataframe read right out of the CSV file
#
raw_df_0 = pd.read_csv('fdata.csv')
raw_df_0.index = raw_df_0['date']
del raw_df_0['date']

#
# series v1
# 
# map zeroes to NaN which makes the interpolation possible
#
# We "know" that zero is a disallowed value because it doesn't make
# sense in context of the data. Therefore, it is safe to replace
# zeroes with NaN
#
zero_df_1 = raw_df_0.copy(deep=True)
print(zero_df_1)

#
# series v2
#
# replace the zeroes with nan
#
nan_df_2 = zero_df_1.copy(deep=True)
nan_df_2['weight'] = nan_df_2['weight'].replace(0, np.nan)

#
# series v3
#
# linearly interpolate missing (NaN) data
#
interp_df_3 = nan_df_2.copy(deep=True)
interp_df_3.interpolate(inplace=True)

#
# series 4
#
# compute the diffs in the series
#
# delta_w[n] = w[n] - w[n-1]
#
diff_df_4 = interp_df_3.copy(deep=True)
diffs = []
for i, w in enumerate(diff_df_4['weight']):
  if i > 0:
    print(i, w - diff_df_4['weight'][i-1])
    diffs.append(w - diff_df_4['weight'][i-1])
print(diffs)
# make same length with offset of one
diffs = [0] + diffs
# assign diffs to a new column in the new dataframe and get rid of the
# original one
diff_df_4['diffs'] = diffs
del diff_df_4['weight']

#
# into the REPL for interactive playing with the data
# 
import IPython; IPython.embed()

lg.info("completed interactive session ... exiting")
