#!/usr/local/uvcdat/1.3.1/bin/python

# Defines plot types and their inputs 

#from fileio.filetable import basic_filetable
#import frontend.options
import cdms2, cdutil, vcs


class basic_plot_type():
   _title = ''
   _xaxis_label = ''
   _yaxis_label = ''
   _type = ''
   _plot_object = None
   _plot = None
   def clear(self):
      self._plot_object.clear()

class line_plot(basic_plot_type):
   _type='Yxvsx'

   def __init__(self, title, xlabel, ylabel, xval, yval, vcs_obj):
      _title = title
      _xaxis_label = xlabel
      _yaxis_label = ylabel
      self._plot_object = vcs_obj

   def gen_plot(self, varx, fname = None):
#      self._plot_object.set(self._type, 'quick')
      if fname == None:
         bg = 0
      else:
         bg=1
      self._plot_object.yxvsx(varx, long_name=self._title, bg=bg)
#      self.plot_object.plot(var, long_name=self._title, bg=bg)
      if fname != None:
         self._plot_object.png(fname)


class contour_plot(basic_plot_type):
   _type='Isofill'

   def __init__(self, title, xlabel, ylabel, xval, yval, vcs_obj):
      _title = title
      _xaxis_label = xlabel
      _yaxis_label = ylabel
      self._plot_object = vcs_obj

   def gen_plot(self, var, fname = None):
      self._plot_object.set(self._type, 'quick')
      if fname == None:
         bg=0
      else:
         bg=1
      print 'title: ', self._title
      self._plot_object.plot(var, long_name=self._title, bg=bg)
      if fname != None:
         self._plot_object.png(fname)


if __name__ == '__main__':
   import cdms2, cdutil, vcs, cdutil.times
   f = cdms2.open('/Users/bs1/data/2yr/tropics_warming_th_q.clm2.h0.0f853ce345620bb77c4f54611bbda495.xml')
   months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
   tg = f('TG')
   tg_mar = cdutil.MAR.climatology(tg)
   try:
      v=vcs.init()
   except:
      print 'Couldnt initialize vcs. likely your X server is hosed'
      quit()
   p = contour_plot('title', 'xlabel', 'ylabel', None, None, v)
   p.gen_plot(tg_mar, 'tg_mar.png')
   p.clear()

   tlai = f('TLAI')
   data = []
   for m in months:
      seas = cdutil.times.Seasons(m)
      tlai_avg = seas(tlai)
      g_avg = cdutil.averager(tlai_avg, axis = 'xy')
      data.append(float(g_avg.data[0]))

   p = line_plot('title', 'xlabel', 'ylabel', None, None, v)
   p.gen_plot(data, 'tlai_year.png')
    
   print 'Done'
   quit()
   
