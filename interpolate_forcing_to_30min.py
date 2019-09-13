#!/usr/bin/env python
"""
Input forcing for CABLE is 3 hrly, linearly interpolate it to 30 mins.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (11.09.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import xarray as xr
import numpy as np
import sys
import glob
import subprocess

def interpolate_forcing(fpath, var, output_dir, years=None):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_dir_var = os.path.join(output_dir, var)
    if not os.path.exists(output_dir_var):
        os.makedirs(output_dir_var)

    # Do all the files in the directory...?
    if years is None:
        files = glob.glob(os.path.join(fpath, "%s/*.nc") % (var))
        years = np.sort(np.asarray([int(f[-7:-3]) for f in files]))

    last_year = years[-1]
    start_date = "%d-01-01,00:00:00" % (years[0])

    for year in years:
        print(year)
        fn = os.path.join(fpath,
                          "%s/GSWP3.BC.%s.3hrMap.%d.nc" % (var, var, year))

        # We can just interpolate between the current year and the next year...
        if year != last_year:

            # Get the first day of the next year day
            first_date = "%d-01-01" % (year)
            tmp_fn = os.path.join(output_dir_var, "tmp.nc")
            cmd = "cdo seldate,%s %s %s" % (first_date, fn, tmp_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error getting the first day")

            # merge extra day into file, so we can interpolate across the final
            # timestep which ends 21:00
            tmp2_fn = os.path.join(output_dir_var, "tmp2.nc")
            cmd = "cdo mergetime %s %s %s" % (fn, tmp_fn, tmp2_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error merging new file")

            # interpolate to 30 min
            out_fn = os.path.join(output_dir_var,
                                  "GSWP3.BC.%s.3hrMap.%d.nc" % (var, year))
            start_date = "%d-01-01,00:00:00" % (year)
            cmd = "cdo inttime,%s,30minutes %s %s" % \
                    (start_date, tmp2_fn, out_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error interpolating file")

            os.remove(tmp_fn)
            os.remove(tmp2_fn)

        # There is no next year, so we need to use the same day again as a fudge
        # to interpolate across the final three hours
        else:

            # Get the last day of the file
            last_date = "%d-12-31" % (year)
            tmp_fn = os.path.join(output_dir_var, "tmp.nc")
            cmd = "cdo seldate,%s %s %s" % (last_date, fn, tmp_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error getting the last day")

            # change the date so that we pretend it comes from the next year
            tmp2_fn = os.path.join(output_dir_var, "tmp2.nc")
            new_date = "%d-01-01,00:00:00" % (year + 1)
            cmd = "cdo settaxis,%s,3hours %s %s" % (new_date, tmp_fn, tmp2_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error changing the date file")

            # merge extra day into file, so we can interpolate across the final
            # timestep which ends 21:00
            tmp3_fn = os.path.join(output_dir_var, "tmp3.nc")
            cmd = "cdo mergetime %s %s %s" % (fn, tmp2_fn, tmp3_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error merging new file")

            # interpolate to 30 min
            tmp4_fn = os.path.join(output_dir_var, "tmp4.nc")
            start_date = "%d-01-01,00:00:00" % (year)
            cmd = "cdo inttime,%s,30minutes %s %s" % \
                    (start_date, tmp3_fn, tmp4_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error interpolating file")

            # Drop the final date from the dummy extra year
            out_fn = os.path.join(output_dir_var,
                                  "GSWP3.BC.%s.3hrMap.%d.nc" % (var, year))
            start_date = "%d-01-01" % (year)
            end_date = "%d-12-31" % (year)
            cmd = "cdo seldate,%s,%s %s %s" % \
                    (start_date, end_date, tmp4_fn, out_fn)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise Exception("Error dropping final day")


            os.remove(tmp_fn)
            os.remove(tmp2_fn)
            os.remove(tmp3_fn)
            os.remove(tmp4_fn)


if __name__ == "__main__":

    #years = np.arange(1995, 2010+1)
    years = np.arange(1995, 1996) # Test one year

    (sysname, nodename, release, version, machine) = os.uname()
    if "Mac" in nodename or "imac" in nodename:
        fpath = "/Users/mdekauwe/Desktop/GSWP3"
    else:
        fpath = "/g/data1/wd9/MetForcing/Global/GSWP3_2017/"

    output_dir = "GSWP3_interpolated"

    # Expecting var to be supplied on cmd line, e.g.
    # $ python interpolate_forcing_to_30min.py "Tair"
    if len(sys.argv) < 2:
        raise TypeError("Expecting var name to be supplied on cmd line!")
    var = sys.argv[1]

    interpolate_forcing(fpath, var, output_dir, years)
