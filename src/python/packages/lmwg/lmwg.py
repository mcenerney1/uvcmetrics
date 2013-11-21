from diagnostic_groups import *
from computation.reductions import *
#from metrics.frontend.uvcdat import *
from unidata import udunits
import cdutil.times
from defines import *

### Properties for a graph:
## Axis name/type
## Graph type
## Units
## Data
## Title
## Any others?

class LMWG(BasicDiagnosticGroup):
   """ This is mostly the AMWG.py code, but I am trying to make as many
       'properties' based plots as I can rather than hardcoding each
       set (beyond derived variables lists, etc)
   """

   def __init__(self):
      pass
   def list_variables( self, filetable1, filetable2=None, diagnostic_set_name="" ):
      if diagnostic_set_name!="":
         dset = self.list_diagnostic_sets().get( diagnostic_set_name, None )
         if dset is None:
            return self._list_variables( filetable1, filetable2 )
         else:   # Note that dset is a class not an object.
            return dset._list_variables( filetable1, filetable2 )
      else:
         return self._list_variables( filetable1, filetable2 )
   @staticmethod
   def _list_variables( filetable1, filetable2=None, diagnostic_set_name="" ):
      return BasicDiagnosticGroup._list_variables( filetable1, filetable2, diagnostic_set_name )
   def list_diagnostic_sets( self ):
      l = []
      for key in package_ids:
         l.append({key:package_sets[key]['name']})
      return l
#        plot_sets = lmwg_plot_spec.__subclasses__()
#        return { aps.name:aps for aps in plot_sets if hasattr(aps,'name') }

class lmwg_plot_spec(plot_spec):
    package = LMWG  # Note that this is a class not an object.
    @staticmethod
    def _list_variables( filetable1, filetable2=None ):
        return lmwg_plot_spec.package._list_variables( filetable1, filetable2, "lmwg_plot_spec" )

# plot set classes we need which I haven't done yet:
# What I'd like to be able to do is say:
# Plot set 2 - Horizontal Contour Plots for plot type
#            - Seasonal and ANN climatologies
#            - Normal vars
#            - Derived vars
#            - Generate plots

class lmwg_plot_set2(lmwg_plot_spec):
    """represents one plot from lmwg Diagnostics Plot Set 2.
    Each such plot is a set of three contour plots: one each for model output, observations, and
    the difference between the two.  A plot's x-axis is longitude and its y-axis is the latitude;
    normally a world map will be overlaid.
    """
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string identifying the variable to be plotted, e.g. 'TREFHT'.
        seasonid is a string such as 'DJF'."""
        plot_spec.__init__(self,seasonid)
        self.plottype = 'Isofill'
        self.season = cdutil.times.Seasons(self._seasonid)  # note that self._seasonid can differ froms seasonid

        self._var_baseid = '_'.join([varid,'set2'])   # e.g. TREFHT_set5
        self.plot1_id = filetable1._id+'_'+varid+'_'+seasonid
        self.plot2_id = filetable2._id+'_'+varid+'_'+seasonid
        self.plot3_id = filetable1._id+' - '+filetable2._id+'_'+varid+'_'+seasonid
        self.plotall_id = filetable1._id+'_'+filetable2._id+'_'+varid+'_'+seasonid

        if not self.computation_planned:
            self.plan_computation( filetable1, filetable2, varid, seasonid )
    def plan_computation( self, filetable1, filetable2, varid, seasonid ):
        self.reduced_variables = {
            varid+'_1': reduced_variable(
                variableid=varid, filetable=filetable1, reduced_var_id=varid+'_1',
                reduction_function=(lambda x,vid: reduce2latlon_seasonal( x, self.season, vid ) ) ),
            varid+'_2': reduced_variable(
                variableid=varid, filetable=filetable2, reduced_var_id=varid+'_2',
                reduction_function=(lambda x,vid: reduce2latlon_seasonal( x, self.season, vid ) ) )
            }
        self.derived_variables = {'PREC': derived_var(
         vid ='PREC',
         inputs=[['RAIN', 'SNOW']],
         outputs=[],
         func=sumvarlist),
        'TOTRUNOFF': derived_var(
         vid = 'TOTRUNOFF',
         inputs=[['QOVER', 'QDRAI', 'QRGWL']],
         outputs=[],
         func=sumvarlist),
        'LHEAT' : derived_var(
         vid = 'LHEAT',
         inputs=[['FCTR', 'FCEV', 'FGEV']],
         outputs=[],
         func=sumvarlist),
        'ET': derived_var(
         vid = 'ET',
         inputs=[['QSOIL', 'QVEGE', 'QVEGT']],
         outputs=[],
         func=sumvarlist),
        'PminusE': derived_var(
         vid = 'PminusE',
         inputs=['PREC', 'ET'],
         outputs=[],
         func=aminusb),
        'ASA' : derived_var(
         vid = 'ASA',
         inputs=[['FSR', 'FSDS']],
         outputs=[],
         func=adivb),
        'EVAPFRAC': derived_var(
         vid = 'EVAPFRAC',
         inputs=[['LHEAT', 'FSH']],
         outputs=[],
         func=adivapb)}
        self.single_plotspecs = {
            self.plot1_id: plotspec(
                vid = varid+'_1',
                zvars = [varid+'_1'],  zfunc = (lambda z: z),
                plottype = self.plottype ),
            self.plot2_id: plotspec(
                vid = varid+'_2',
                zvars = [varid+'_2'],  zfunc = (lambda z: z),
                plottype = self.plottype ),
            self.plot3_id: plotspec(
                vid = varid+' diff',
                zvars = [varid+'_1',varid+'_2'],  zfunc = aminusb_2ax,
                plottype = self.plottype )
            }
        self.composite_plotspecs = {
            self.plotall_id: [ self.plot1_id, self.plot2_id, self.plot3_id ]            
            }
        self.computation_planned = True
    def _results(self):
        results = plot_spec._results(self)
        if results is None: return None
        return self.plotspec_values[self.plotall_id]


