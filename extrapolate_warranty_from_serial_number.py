#!/usr/bin/env python


#   This script was written to create an extension attribute to the jss
#   that estimates warranty information extrapolated from codes included
#   in mac serial numbers. 

#   Apple has blocked programatic access to its warranty lookup site.
#   As a result, dates provided by this script are unverified estimates only.

#   Much of the code below is cribbed from Michael Lynn's warranty module.
#   Use at your own risk. 


#   Author:     Andrew Thomson
#   Date:       11-10-2015


import subprocess, datetime, dateutil.parser, time


def apple_year_offset(dateobj, years=0):
    # Convert to a maleable format
    mod_time = dateobj.timetuple()
    # Offset year by number of years
    mod_time = time.struct_time(tuple([mod_time[0]+years]) + mod_time[1:])
    # Convert back to a datetime obj
    return datetime.datetime.fromtimestamp(int(time.mktime(mod_time)))


def estimated_manufacture_date(serial):
    est_date = u''
    if 10 < len(serial) < 13:
        if len(serial) == 11:
            # Old format
            year = serial[2].lower()
            est_year = 2000 + '   3456789012'.index(year)
            week = int(serial[3:5]) - 1
            year_time = datetime.date(year=est_year, month=1, day=1)
            if (week):
                week_dif = datetime.timedelta(weeks=week)
                year_time += week_dif
            est_date = u'' + year_time.strftime('%Y-%m-%d')
        else:
            # New format
            alpha_year = 'cdfghjklmnpqrstvwxyz'
            year = serial[3].lower()
            est_year = 2010 + (alpha_year.index(year) / 2)
            # 1st or 2nd half of the year
            est_half = alpha_year.index(year) % 2
            week = serial[4].lower()
            alpha_week = ' 123456789cdfghjklmnpqrtvwxy'
            est_week = alpha_week.index(week) + (est_half * 26) - 1
            year_time = datetime.date(year=est_year, month=1, day=1)
            if (est_week):
                week_dif = datetime.timedelta(weeks=est_week)
                year_time += week_dif
            est_date = u'' + year_time.strftime('%Y-%m-%d')
    return est_date


def estimated_warranty_status(manufacture_date, warranty_date, applecare_date):
    if (datetime.datetime.now() > dateutil.parser.parse(applecare_date)):
        warranty_status = u'EXPIRED'
    elif (datetime.datetime.now() > dateutil.parser.parse(warranty_date)):
        warranty_status = u'APPLECARE'
    else:
        warranty_status = u'LIMITED'
    return warranty_status


#   get serial numer
serial = subprocess.Popen("system_profiler SPHardwareDataType |grep -v tray |awk '/Serial/ {print $4}'", shell=True, stdout=subprocess.PIPE).communicate()[0].strip()

#   get estimated manufacture date
manufacture_date = estimated_manufacture_date(serial)

#   get estimated warranty expiration date
warranty_date = u'' + apple_year_offset(dateutil.parser.parse(manufacture_date), 1).strftime('%Y-%m-%d')

#   get estimated applecare expiration date
applecare_date = u'' + apple_year_offset(dateutil.parser.parse(manufacture_date), 3).strftime('%Y-%m-%d')

#   get estimated warranty status
warranty_status = estimated_warranty_status(manufacture_date, warranty_date, applecare_date)

print "<result>"
print "MANUFACTURE DATE:", manufacture_date
print "WARRANTY DATE:   ", warranty_date
print "APPLECARE DATE:  ", applecare_date
print "WARRANTY STATUS: ", warranty_status
print "</result>"

