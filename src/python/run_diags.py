#!/usr/local/uvcdat/1.3.1/bin/python

# geo_average_min, max, and overall_avg
# annual average years
# annual average values
# geo average data



# High-level functions to convert data to climatology files.
# These are, in my understanding, files which have a time-average of the original
# variables, with the time often restricted to a month or season.
# This is basically a simplified version of plot_data.py.

import cdms2, math, cdutil, genutil, json, os, vcs

try:
   from frontend.options import Options
   from computation.reductions import *
   from fileio.filetable import *
   from fileio.findfiles import *
   from frontend.treeview import TreeView
   from packages.common.plot_types import *
   import packages
except:
   from metrics.frontend.options import Options
   from metrics.computation.reductions import *
   from metrics.fileio.filetable import *
   from metrics.fileio.findfiles import *
   from metrics.frontend.treeview import TreeView
   from metrics.packages.common.plot_types import *
   import metrics.packages


if __name__ == '__main__':
   o = Options()
   o.processCmdLine()
   o.verifyOptions()
   print o._opts['times']

   # At this point, we have our options specified. Need to generate some climatologies and such
   datafiles = []
   filetables = []
   vars = o._opts['vars']
   print vars

   try:
      v = vcs.init()
   except:
      print 'Could not initialize vcs stuff'

   index = 0
   for p in o._opts['path']:
      if(o._opts['verbose'] >= 1):
         print 'Creating datafiles list for path ', p
      datafiles.append(dirtree_datafiles(o))
      if(o._opts['verbose'] >= 1):
         print 'Creating filetable for path ', p
      filetables.append(basic_filetable(datafiles[index], o))
      index = index+1


   print 'Setting up compute steps'
   rvar_list = {}
   vlist = []
   for var in o._opts['vars']:
      print var
      if var in filetables[0]._varindex.keys():
         for seas in o._opts['times']:
            vid = str(var)+'_'+str(seas)
            if seas != 'ANN':
               season = cdutil.times.Seasons([seas])
            else:
               season = seas
            vlist.append(var+'_'+seas)
            key = var+'_'+seas+'_1'
            rvar_list[key] = reduced_variable(variableid = var,
               filetable = filetables[0],
               reduction_function=(lambda x, vid=vid: reduce_time_seasonal(x, season, vid=vid)))
            if len(o._opts['path']) == 2:
               key = var+'_'+seas+'_2'
               rvar_list[key] = reduced_variable(variableid = var,
                  filetable = filetables[1],
                  reduction_function=(lambda x, vid=vid: reduce_time_seasonal(x, season, vid=vid)))
      else:
         print 'Doesnt work with derived vars yet'
         quit()


   print 'Computing reduced variables'
   print vlist
   quit()

   print rvar_list.keys()
   for rv in rvar_list.keys():
      red = rvar_list[rv].reduce(o)
      print type(rvar_list[rv]._reducedvar)

   if len(o._opts['path']) == 2:
      print 'Computing delta variables'
      for vl in vlist:
         key = var+'_'+seas+'_3'
         rvar_list[key] = reduced_variable(variableid = key, filetable=filetables[0], reduction_function=(lambda x: x))
         print 'copying'
         rvar_list[key]._reducedvar = (rvar_list[vl+'_1']._reducedvar - rvar_list[vl+'_2']._reducedvar)
         print 'done copying'
   
   print rvar_list.keys()
#               base = os.path.basename(os.path.splitext(o._opts['path'][0])[0])

            
      # isofill contour plots


   

