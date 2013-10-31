#!/usr/local/uvcdat/1.3.1/bin/python

# High-level functions to convert data to climatology files.
# These are, in my understanding, files which have a time-average of the original
# variables, with the time often restricted to a month or season.
# This is basically a simplified version of plot_data.py.

import cdms2, math

from frontend.options import Options
from io.filetable import *
from io.findfiles import *
import packages


if __name__ == '__main__':
   o = Options()
   o.processCmdLine()

   # At this point, we have our options specified. Need to generate some climatologies and such
   datafiles = []
   filetables = []

   index = 0
   for p in o._opts['path']:
      if(o._opts['verbose'] >= 1):
         print 'Creating datafiles list for path ', p
      datafiles.append(dirtree_datafiles(p))
      if(o._opts['verbose'] >= 1):
         print 'Creating filetable for path ', p
      filetables.append(basic_filetable(datafiles[index]))
      index = index+1



#   print o._opts['path'][0]
#   if(o._opts['filter'] == None):
#      datafiles1 = dirtree_datafiles(o._opts['path'][0])
#   else:
#      datafiles1 = dirtree_datafiles(o._opts['path'][0], o._opts['filter'][0])
#
#   filetable1 = basic_filetable(datafiles1)
   
#   print len(o._opts['path'])

