#!/usr/bin/env python

"""
Wrapper script to send off all the qsub scripts

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (06.09.2019)"
__email__ = "mdekauwe@gmail.com"

import subprocess
import sys
import os

def make_qsub_file(qsub_fname, var):

    s = """
#!/bin/bash

#PBS -m ae
#PBS -P w35
#PBS -q normal
#PBS -M mdekauwe@gmail.com
#PBS -l mem=16GB
#PBS -l ncpus=1
#PBS -l walltime=00:10:00
#PBS -l wd
#PBS -j oe
#PBS -l other=gdata1

module load dot
source activate sci

python src/interpolate_forcing_to_30min.py %s
        """ % (var)

    f = open(qsub_fname, 'w')
    f.write(s)
    f.close()

qsub_dir = "qsub_scripts"
if not os.path.exists(qsub_dir):
    os.makedirs(qsub_dir)

for var in ["LWdown", "PSurf", "SWdown", "Tair", "Qair", \
            "Rainf", "Snowf", "Wind"]:

    qsub_fn = "qsub_scripts/GSWP3_interpolate_%s.sh" % (var)
    make_qsub_file(qsub_fn, var)

    qs_cmd = "qsub %s" % (qsub_fn)
    error = subprocess.call(qs_cmd, shell=True)
    if error is 1:
        print("Job failed to submit")
