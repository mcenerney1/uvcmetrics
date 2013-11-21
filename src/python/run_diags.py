#!/usr/local/uvcdat/1.3.1/bin/python

# geo_average_min, max, and overall_avg
# annual average years
# annual average values
# geo average data



# High-level functions to convert data to climatology files.
# These are, in my understanding, files which have a time-average of the original
# variables, with the time often restricted to a month or season.
# This is basically a simplified version of plot_data.py.

import cdms2, math, cdutil, genutil, json

from frontend.options import Options
from computation.reductions import *
from fileio.filetable import *
from fileio.findfiles import *
from frontend.treeview import TreeView
import packages


# This is all entirely too complicated for what it does.
class climatology_variable(reduced_variable):
   def __init__(self, varname, filetable, seasonname='ANN'):
      print varname
      vid = 'reduced_'+varname
      if seasonname =='ANN':
         reduced_variable.__init__(self,
            variableid=varname, filetable=filetable,
            reduction_function=(lambda x, vid=vid: reduce_time(x, vid=vid)))
      else:
         season = cdutil.times.Seasons([seasonname])
         reduced_variable.__init__(self,
            variableid=varname, filetable=filetable,
            reduction_function=(lambda x, vid=vid: reduce_time_seasonal(x, season, vid=vid)))

if __name__ == '__main__':
   o = Options()
   o.processCmdLine()
   o.verifyOptions()

   # At this point, we have our options specified. Need to generate some climatologies and such
   datafiles = []
   filetables = []
   vars = o._opts['vars']
   print vars

   index = 0
   for p in o._opts['path']:
      if(o._opts['verbose'] >= 1):
         print 'Creating datafiles list for path ', p
      datafiles.append(dirtree_datafiles(p))
      if(o._opts['verbose'] >= 1):
         print 'Creating filetable for path ', p
      filetables.append(basic_filetable(datafiles[index], o))
      index = index+1

   
   for var in o._opts['vars']:
      print var
      print filetables[0]._varindex.keys()
      if var in filetables[0]._varindex.keys():
         for seas in o._opts['times']:
            print 'inner loop'
            vid = str(var)+'_'+str(seas)
            season = cdutil.times.Seasons([seas])
            rvar = reduced_variable(variableid = var,
               filetable = filetables[0],
               reduction_function=(lambda x, vid=vid: reduce_time_seasonal(x, season, vid=vid)))

            print 'Reducing ', var, ' for climatology ', seas
            data = {}
            red = rvar.reduce(o)
            filename = var+"-"+seas+"-climatology.json"
            print 'Writing to ', filename
            g = open(filename, 'w')
            data['geo_average_min'] = red.min()
            data['geo_average_max'] = red.max()
            mv = red.missing_value
            data['missing_value'] = mv
            data['geo_average_data'] = red.data.tolist()
            g_avg = cdutil.averager(red, axis='xy')
            data['geo_average_global'] = g_avg.data.tolist()
            json.dump(data, g, separators=(',',':'))
            g.close()
            print 'Done writing ', filename

   
#   tv = TreeView()
#   dtree = tv.makeTree(o, filetables)
#   tv.dump(filename='flare.json')
   quit()
   

