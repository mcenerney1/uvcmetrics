#!/usr/local/uvcdat/1.3.1/bin/python

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

if __name__ == '__main__':
   o = Options()
#   o.processCmdLine()
#   o.verifyOptions()

   ##### SET THESE BASED ON USER INPUT FROM THE GUI
   o._opts['vars'] = ['TG', 'TV', 'PBOT'] 
   o._opts['path'] = ['/path/to/a/dataset'] 
   o._opts['times'] = ['JAN', 'FEB', 'DJF']
   ### NOTE: 'ANN' won't work for times this way, but that shouldn't be a problem
   #####

   #### This will generate {var}-{times}-climatology.json

   # At this point, we have our options specified. Need to generate some climatologies and such
   datafiles = []
   filetables = []
   vars = o._opts['vars']
#   print vars

   index = 0
   for p in o._opts['path']:
      datafiles.append(dirtree_datafiles(p))
      filetables.append(basic_filetable(datafiles[index], o))
      index = index+1

   for var in o._opts['vars']:
      if var in filetables[0]._varindex.keys():
         for seas in o._opts['times']:
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

   print 'Creating diags tree view JSON file...'
   tv = TreeView()
   dtree = tv.makeTree(o, filetables)
   tv.dump(filename='flare.json')

