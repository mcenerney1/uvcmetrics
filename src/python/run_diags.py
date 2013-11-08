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
from io.filetable import *
from io.findfiles import *
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

   print filetables[0]._varindex.keys()

   for var in o._opts['vars']:
      if var in filetables[0]._varindex.keys():
         for seas in o._opts['times']:
            vid = str(var)+'_'+str(seas)
            season = cdutil.times.Seasons([seas])
            rvar = reduced_variable(variableid = var,
               filetable = filetables[0],
               reduction_function=(lambda x, vid=vid: reduce_time_seasonal(x, season, vid=vid)))
            print 'Reducing ', var, ' for climatology ', seas
            r = rvar.reduce(o)
            d = r.data
            print type(var)
            print r.missing_value
            print r[0][0]
#            print d[150]
            quit()




   quit()


#   print filetables[0].find_files('TG')

#   print '******************************** FIND FILE DONE ********************************'
   reduced_vars = {var+'_'+seas: climatology_variable(var, filetables[0], seas)
                  for seas in o._opts['times']
                  for var in o._opts['vars']}
                  #for seas in ['ANN', 'DJF'] #, 'SON', 'MAM', 'JJA', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG','SEP', 'OCT', 'NOV', 'DEC']

   print reduced_vars

   varvals = {}
   varkeys = reduced_vars.keys()
   data = {}

   for key in varkeys:
      print 'Reducing ', key
      varvals[key] = reduced_vars[key].reduce(o)
      var = reduced_vars[key]
      filename = key+"_test.json"
      print 'Writing ', filename
      if varvals[key] is not None:
         g = open(filename, 'w')
         print varvals[key][0][0]
         data['geo_average_min'] = varvals[key].min()
         data['geo_average_max'] = varvals[key].max()
         mv = varvals[key].missing_value
         data['missing_value'] = mv
         d = varvals[key].filled(mv).tolist()
#         d = varvals[key].data
#         e = d.filled(mv).tolist()
#         print e[0][0]
#         d = varvals[key].data.tolist()[0]

#         d = (varvals[key].data).filled(mv).tolist()

#         d = varvals[key].filled(mv).tolist()
#         print d[0]
         data['geo_average_data'] = d
#         data['geo_average_data'] = varvals[key].tolist()
         json.dump(data, g, separators=(',',':'))
         g.close()
#         g = cdms2.open(filename, 'w')
#         g.write(varvals[key])
#         g.close()

#   reduced_variables = {
#      'tg_1': reduced_variable(
#         variableid='TG', filetable=filetable1,
#         reduction_function=(lambda x, vid=None, x)),
#      'pbot_1': reduced_variable(
#         variableid='PBOT', filetable=filetable1,
#         reduction_function=(lambda x, vid=None, x))}}



#   print o._opts['path'][0]
#   if(o._opts['filter'] == None):
#      datafiles1 = dirtree_datafiles(o._opts['path'][0])
#   else:
#      datafiles1 = dirtree_datafiles(o._opts['path'][0], o._opts['filter'][0])
#
#   filetable1 = basic_filetable(datafiles1)
   
#   print len(o._opts['path'])

