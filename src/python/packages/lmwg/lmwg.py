from diagnostic_groups import *
from computation.reductions import *
#from metrics.frontend.uvcdat import *
from unidata import udunits
import cdutil.times
from defines import *

class LMWG(BasicDiagnosticGroup):
   """This class sets up all of the plot types in LMWG specifically. Hopefully
      someday this can be done as a set of properties per plot rather than
      hardcoding like this which makes it difficult to reuse code between
      realms/packages/sets"""

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
         outputs=['nothing'],
         func=sumvarlist),
        'TOTRUNOFF': derived_var(
         vid = 'TOTRUNOFF',
         inputs=[['QOVER', 'QDRAI', 'QRGWL']],
         outputs=['nothing'],
         func=sumvarlist),
        'LHEAT' : derived_var(
         vid = 'LHEAT',
         inputs=[['FCTR', 'FCEV', 'FGEV']],
         outputs=['nothing'],
         func=sumvarlist),
        'ET': derived_var(
         vid = 'ET',
         inputs=[['QSOIL', 'QVEGE', 'QVEGT']],
         outputs=['nothing'],
         func=sumvarlist),
        'PminusE': derived_var(
         vid = 'PminusE',
         inputs=['PREC', 'ET'],
         outputs=['nothing'],
         func=aminusb),
        'ASA' : derived_var(
         vid = 'ASA',
         inputs=[['FSR', 'FSDS']],
         outputs=['nothing'],
         func=adivb),
        'EVAPFRAC': derived_var(
         vid = 'EVAPFRAC',
         inputs=[['LHEAT', 'FSH']],
         outputs=['nothing'],
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
class lmwg_plot_set1(lmwg_plot_spec):
    pass
class lmwg_plot_set4a(lmwg_plot_spec):
    pass
class lmwg_plot_set7(lmwg_plot_spec):
    pass
class lmwg_plot_set8(lmwg_plot_spec):
    pass
class lmwg_plot_set9(lmwg_plot_spec):
    pass
class lmwg_plot_set10(lmwg_plot_spec):
    pass
class lmwg_plot_set11(lmwg_plot_spec):
    pass
class lmwg_plot_set12(lmwg_plot_spec):
    pass
class lmwg_plot_set13(lmwg_plot_spec):
    pass
class lmwg_plot_set14(lmwg_plot_spec):
    pass
class lmwg_plot_set15(lmwg_plot_spec):
    pass


class lmwg_plot_set2(lmwg_plot_spec):
    """represents one plot from lmwg Diagnostics Plot Set 2
    Each such plot is a page consisting of two to four plots.  The horizontal
    axis is latitude and the vertical axis is heat or fresh-water transport.
    Both model and obs data is plotted, sometimes in the same plot.
    The data presented is averaged over everything but latitude.
    """
    name = ' 2- Line Plots of Annual Implied Northward Transport'
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string identifying the derived variable to be plotted, e.g. 'Ocean_Heat'.
        The seasonid argument will be ignored."""
        plot_spec.__init__(self,seasonid)
        self.plottype='Yxvsx'
        vars = self._list_variables(filetable1,filetable2)
        if varid not in vars:
            print "In lmwg_plot_set2 __init__, ignoring varid input, will compute Ocean_Heat"
            varid = vars[0]
        self._var_baseid = '_'.join([varid,'set2'])   # e.g. Ocean_Heat_set2
        print "Warning: lmwg_plot_set2 only uses NCEP obs, and will ignore any other obs specification."
        if not self.computation_planned:
            self.plan_computation( filetable1, filetable2, varid, seasonid )
    @staticmethod
    def _list_variables( self, filetable1=None, filetable2=None ):
        return ['Ocean_Heat']
    def plan_computation( self, filetable1, filetable2, varid, seasonid ):
        # CAM variables needed for heat transport: (SOME ARE SUPERFLUOUS <<<<<<)
        # FSNS, FLNS, FLUT, FSNTOA, FLNT, FSNT, SHFLX, LHFLX,
        self.reduced_variables = {
            'FSNS_1': reduced_variable(
                variableid='FSNS',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'FSNS_ANN_latlon_1': reduced_variable(
                variableid='FSNS',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'FLNS_1': reduced_variable(
                variableid='FLNS',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'FLNS_ANN_latlon_1': reduced_variable(
                variableid='FLNS',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'FLUT_ANN_latlon_1': reduced_variable(
                variableid='FLUT',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'FSNTOA_ANN_latlon_1': reduced_variable(
                variableid='FSNTOA',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'FLNT_1': reduced_variable(
                variableid='FLNT',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'FLNT_ANN_latlon_1': reduced_variable(
                variableid='FLNT',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'FSNT_1': reduced_variable(
                variableid='FSNT',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'FSNT_ANN_latlon_1': reduced_variable(
                variableid='FSNT',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'QFLX_1': reduced_variable(
                variableid='QFLX',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'SHFLX_1': reduced_variable(
                variableid='SHFLX',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
            'SHFLX_ANN_latlon_1': reduced_variable(
                variableid='SHFLX',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'LHFLX_ANN_latlon_1': reduced_variable(
                variableid='LHFLX',
                filetable=filetable1,
                reduction_function=reduce2latlon ),
            'OCNFRAC_ANN_latlon_1': reduced_variable(
                variableid='OCNFRAC',
                filetable=filetable1,
                reduction_function=reduce2latlon )
            }
        self.derived_variables = {
            'CAM_HEAT_TRANSPORT_ALL_1': derived_var(
                vid='CAM_HEAT_TRANSPORT_ALL_1',
                inputs=['FSNS_ANN_latlon_1', 'FLNS_ANN_latlon_1', 'FLUT_ANN_latlon_1',
                        'FSNTOA_ANN_latlon_1', 'FLNT_ANN_latlon_1', 'FSNT_ANN_latlon_1',
                        'SHFLX_ANN_latlon_1', 'LHFLX_ANN_latlon_1', 'OCNFRAC_ANN_latlon_1' ],
                outputs=['atlantic_heat_transport','pacific_heat_transport',
                         'indian_heat_transport', 'global_heat_transport' ],
                func=oceanic_heat_transport ),
            'NCEP_OBS_HEAT_TRANSPORT_ALL_2': derived_var(
                vid='NCEP_OBS_HEAT_TRANSPORT_ALL_2',
                inputs=[],
                outputs=('latitude', ['atlantic_heat_transport','pacific_heat_transport',
                                      'indian_heat_transport', 'global_heat_transport' ]),
                func=(lambda: ncep_ocean_heat_transport(filetable2) ) )
            }
        self.single_plotspecs = {
            'CAM_NCEP_HEAT_TRANSPORT_GLOBAL': plotspec(
                vid='CAM_NCEP_HEAT_TRANSPORT_GLOBAL',
                x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
                y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
                y1func=(lambda y: y[3]),
                x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
                y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
                y2func=(lambda y: y[1][3]),
                plottype = self.plottype  ),
            'CAM_NCEP_HEAT_TRANSPORT_PACIFIC': plotspec(
                vid='CAM_NCEP_HEAT_TRANSPORT_PACIFIC',
                x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
                y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
                y1func=(lambda y: y[0]),
                x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
                y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
                y2func=(lambda y: y[1][0]),
                plottype = self.plottype  ),
            'CAM_NCEP_HEAT_TRANSPORT_ATLANTIC': plotspec(
                vid='CAM_NCEP_HEAT_TRANSPORT_ATLANTIC',
                x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
                y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
                y1func=(lambda y: y[0]),
                x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
                y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
                y2func=(lambda y: y[1][1]),
                plottype = self.plottype  ),
            'CAM_NCEP_HEAT_TRANSPORT_INDIAN': plotspec(
                vid='CAM_NCEP_HEAT_TRANSPORT_INDIAN',
                x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
                y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
                y1func=(lambda y: y[0]),
                x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
                y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
                y2func=(lambda y: y[1][2]),
                plottype = self.plottype  )
            }
        self.composite_plotspecs = {
            'CAM_NCEP_HEAT_TRANSPORT_ALL':
                ['CAM_NCEP_HEAT_TRANSPORT_GLOBAL','CAM_NCEP_HEAT_TRANSPORT_PACIFIC',
                 'CAM_NCEP_HEAT_TRANSPORT_ATLANTIC','CAM_NCEP_HEAT_TRANSPORT_INDIAN']
            }
        self.computation_planned = True

    def _results(self):
        results = plot_spec._results(self)
        if results is None: return None
        return self.plotspec_values['CAM_NCEP_HEAT_TRANSPORT_ALL']


class lmwg_plot_set3(lmwg_plot_spec):
    """represents one plot from lmwg Diagnostics Plot Set 3.
    Each such plot is a pair of plots: a 2-line plot comparing model with obs, and
    a 1-line plot of the model-obs difference.  A plot's x-axis is latitude, and
    its y-axis is the specified variable.  The data presented is a climatological mean - i.e.,
    time-averaged with times restricted to the specified season, DJF, JJA, or ANN."""
    # N.B. In plot_data.py, the plotspec contained keys identifying reduced variables.
    # Here, the plotspec contains the variables themselves.
    name = ' 3- Line Plots of  Zonal Means'
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string, e.g. 'TREFHT'.  Seasonid is a string, e.g. 'DJF'."""
        plot_spec.__init__(self,seasonid)
        self.season = cdutil.times.Seasons(self._seasonid)  # note that self._seasonid can differ froms seasonid
        self._var_baseid = '_'.join([varid,seasonid,'set3'])   # e.g. CLT_DJF_set3
        if not self.computation_planned:
            self.plan_computation( filetable1, filetable2, varid, seasonid )
    def plan_computation( self, filetable1, filetable2, varid, seasonid ):
        y1var = reduced_variable(
            variableid=varid,
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,self.season,vid=vid)) )
        self.reduced_variables[varid+'_1'] = y1var
        y1var._vid = varid+'_1'
        y2var = reduced_variable(
            variableid=varid,
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,self.season,vid=vid)) )
        self.reduced_variables[varid+'_2'] = y2var
        y2var._vid = varid+'_2'
        self.plot_a = basic_two_line_plot( y1var, y2var )
        vid = '_'.join([self._var_baseid,filetable1._id,filetable2._id,'diff'])
        # ... e.g. CLT_DJF_set3_CAM456_NCEP_diff
        self.plot_b = one_line_diff_plot( y1var, y2var, vid )
        self.computation_planned = True
    def _results(self):
        # At the moment this is very specific to plot set 3.  Maybe later I'll use a
        # more general method, to something like what's in plot_data.py, maybe not.
        # later this may be something more specific to the needs of the UV-CDAT GUI
        results = plot_spec._results(self)
        if results is None: return None
        y1var = self.plot_a.y1vars[0]
        y2var = self.plot_a.y2vars[0]
        #y1val = y1var.reduce()
        y1val = self.variable_values[y1var._vid]
        if y1val is None: return None
        y1unam = y1var._filetable._id  # unique part of name for y1, e.g. CAM456
        y1val.id = '_'.join([self._var_baseid,y1unam])  # e.g. CLT_DJF_set3_CAM456
        #y2val = y2var.reduce()
        y2val = self.variable_values[y2var._vid]
        if y2val is None: return None
        y2unam = y2var._filetable._id  # unique part of name for y2, e.g. NCEP
        y2val.id = '_'.join([self._var_baseid,y2unam])  # e.g. CLT_DJF_set3_NCEP
        ydiffval = apply( self.plot_b.yfunc, [y1val,y2val] )
        ydiffval.id = '_'.join([self._var_baseid, y1var._filetable._id, y2var._filetable._id,
                                'diff'])
        # ... e.g. CLT_DJF_set3_CAM456_NCEP_diff
        plot_a_val = uvc_plotspec(
            [y1val,y2val],'Yxvsx', labels=[y1unam,y2unam],
            title=' '.join([self._var_baseid,y1unam,'and',y2unam]))
        plot_b_val = uvc_plotspec(
            [ydiffval],'Yxvsx', labels=['difference'],
            title=' '.join([self._var_baseid,y1unam,'-',y2unam]))
        return [ plot_a_val, plot_b_val ]

class lmwg_plot_set4(lmwg_plot_spec):
    """represents one plot from lmwg Diagnostics Plot Set 4.
    Each such plot is a set of three contour plots: one each for model output, observations, and
    the difference between the two.  A plot's x-axis is latitude and its y-axis is the level,
    measured as pressure.  The model and obs plots should have contours at the same values of
    their variable.  The data presented is a climatological mean - i.e.,
    time-averaged with times restricted to the specified season, DJF, JJA, or ANN."""
    # N.B. In plot_data.py, the plotspec contained keys identifying reduced variables.
    # Here, the plotspec contains the variables themselves.
    name = ' 4- Vertical Contour Plots Zonal Means'
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string, e.g. 'TREFHT'.  Seasonid is a string, e.g. 'DJF'.
        At the moment we assume that data from filetable1 has CAM hybrid levels,
        and data from filetable2 has pressure levels."""
        plot_spec.__init__(self,seasonid)
        self.season = cdutil.times.Seasons(self._seasonid)  # note that self._seasonid can differ froms seasonid
        self._var_baseid = '_'.join([varid,seasonid,'set4'])   # e.g. CLT_DJF_set4
        if not self.computation_planned:
            self.plan_computation( filetable1, filetable2, varid, seasonid )
    def plan_computation( self, filetable1, filetable2, varid, seasonid ):
        rv1 = reduced_variable(
            variableid=varid,
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2levlat_seasonal(x,self.season,vid=vid)) )
        self.reduced_variables[varid+'_1'] = rv1
        rv2 = reduced_variable(
            variableid=varid,
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2levlat_seasonal(x,self.season,vid=vid)) )
        self.reduced_variables[varid+'_2'] = rv2
        hyam = reduced_variable(      # hyam=hyam(lev)
            variableid='hyam', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) )
        self.reduced_variables['hyam'] = hyam
        hybm = reduced_variable(      # hyab=hyab(lev)
            variableid='hybm', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) )
        self.reduced_variables['hybm'] = hybm
        ps = reduced_variable(
            variableid='PS', filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,self.season,vid=vid)) )
        self.reduced_variables['ps'] = ps
        vid1='_'.join([varid,seasonid,'levlat'])
        vv1 = derived_var(
            vid=vid1, inputs=[varid+'_1', 'hyam', 'hybm', 'ps', varid+'_2'], func=verticalize )
        vv1._filetable = filetable1  # so later we can extract the filetable id for labels
        self.derived_variables[vid1] = vv1
        vv2 = rv2
        vv2._vid = varid+'_2'        # for lookup conventience in results() method
        vv2._filetable = filetable2  # so later we can extract the filetable id for labels

        self.plot_a = contour_plot( vv1, xfunc=latvar, yfunc=levvar, ya1func=heightvar )
        self.plot_b = contour_plot( vv2, xfunc=latvar, yfunc=levvar, ya1func=heightvar )
        vid = '_'.join([self._var_baseid,filetable1._id,filetable2._id,'diff'])
        # ... e.g. CLT_DJF_set4_CAM456_NCEP_diff
        self.plot_c = contour_diff_plot( vv1, vv2, vid, xfunc=latvar_min, yfunc=levvar_min,
                                         ya1func=(lambda y1,y2: heightvar(levvar_min(y1,y2))))
        self.computation_planned = True
    def _results(self):
        # At the moment this is very specific to plot set 4.  Maybe later I'll use a
        # more general method, to something like what's in plot_data.py, maybe not.
        # later this may be something more specific to the needs of the UV-CDAT GUI
        results = plot_spec._results(self)
        if results is None: return None
        zavar = self.plot_a.zvars[0]
        zaval = self.variable_values[ zavar._vid ]
        if zaval is None: return None
        zaunam = zavar._filetable._id  # unique part of name for y1, e.g. CAM456
        zaval.id = '_'.join([self._var_baseid,zaunam])  # e.g. CLT_DJF_set4_CAM456

        zbvar = self.plot_b.zvars[0]
        #zbval = zbvar.reduce()
        zbval = self.variable_values[ zbvar._vid ]
        if zbval is None: return None
        zbunam = zbvar._filetable._id  # unique part of name for y1, e.g. OBS123
        zbval.id = '_'.join([self._var_baseid,zbunam])  # e.g. CLT_DJF_set4_OBS123

        z1var = self.plot_c.zvars[0]
        z2var = self.plot_c.zvars[1]
        z1val = self.variable_values[ z1var._vid ]
        z2val = self.variable_values[ z2var._vid ]
        z1unam = z1var._filetable._id  # unique part of name for y1, e.g. OBS123
        z1val.id = '_'.join([self._var_baseid,z1unam])  # e.g. CLT_DJF_set4_OBS123
        z2unam = z1var._filetable._id  # unique part of name for y1, e.g. OBS123
        z2val.id = '_'.join([self._var_baseid,z2unam])  # e.g. CLT_DJF_set4_OBS123
        zdiffval = apply( self.plot_c.zfunc, [z1val,z2val] )
        if zdiffval is None: return None
        zdiffval.id = '_'.join([self._var_baseid, z1var._filetable._id, z2var._filetable._id,
                                'diff'])
        # ... e.g. CLT_DJF_set4_CAM456_OBS123_diff
        plot_a_val = uvc_plotspec(
            [zaval],'Isofill', labels=[zaunam],
            title= zaunam )
        plot_b_val = uvc_plotspec(
            [zbval],'Isofill', labels=[zbunam],
            title= zbunam )
        plot_c_val = uvc_plotspec(
            [zdiffval],'Isofill', labels=['difference'],
            title=' '.join([self._var_baseid,z1unam,'-',z2unam]))
        return [ plot_a_val, plot_b_val, plot_c_val ]



class lmwg_plot_set6(lmwg_plot_spec):
    """represents one plot from lmwg Diagnostics Plot Set 6
    **** SO FAR, VECTOR PLOTS ARE NOT DONE; ONLY CONTOUR ****
    The contour plots of set 6 are identical to those of set 5.
    Each such plot is a set of three contour plots: one each for model output, observations, and
    the difference between the two.  A plot's x-axis is longitude and its y-axis is the latitude;
    normally a world map will be overlaid.
    """
    name = ' 6- Horizontal Vector Plots of Seasonal Means'
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string identifying the variable to be plotted, e.g. 'TREFHT'.
        seasonid is a string such as 'DJF'."""
        plot_spec.__init__(self,seasonid)
        self.plottype = 'Isofill'
        self.season = cdutil.times.Seasons(self._seasonid)  # note that self._seasonid can differ froms seasonid

        self._var_baseid = '_'.join([varid,'set6'])   # e.g. TREFHT_set6
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
        self.derived_variables = {}
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


class lmwg_jerry( lmwg_plot_spec ):
    """200 mb heights from variable Z3, for Jerry Potter"""
    name = 'Jerry Potter'
    def __init__( self, filetable1, filetable2, varid, seasonid=None ):
        plot_spec.__init__(self,seasonid)
        self.plottype = 'Isofill'
        self.season = cdutil.times.Seasons(self._seasonid)  # note that self._seasonid can differ froms seasonid

        self._var_baseid = '_'.join([varid,'set6'])   # e.g. TREFHT_set6
        self.plot1_id = filetable1._id+'_'+varid+'_'+seasonid
        self.plotall_id = filetable1._id+'_'+varid+'_'+seasonid

        if not self.computation_planned:
            self.plan_computation( filetable1, filetable2, varid, seasonid )
    @staticmethod
    def _list_variables( self, filetable1=None, filetable2=None ):
        return ['Z3']  # actually any 3-D variable would be ok
    def plan_computation( self, filetable1, filetable2, varid, seasonid ):
        # >>> Instead of reduce2latlon, I want to 
        # (1) Average var (Z3 for now) over time, thus reducing from Z3(time,hlev,lat,lon)
        # to Z3b(hlev,lat,lon) .  This is all that happens at the reduced_variables level.
        # (2) convert Z3b from hybrid (hlev) to pressure (plev) level coordinates- Z3c(plev,lat,lon)
        # This Z3c is a derived variable
        # (3) restrict Z3 to the 200 MB level, thus reducing it to Z3d(lat,lon)
        # This will have to be as the zfunc in the final plot definition.

        # In calling reduce_time_seasonal, I am assuming that no variable has axes other than (time,
        # lev,lat,lon).  If there were another axis, then we'd need a new function which reduces it.
        self.reduced_variables = {
            varid+'_1': reduced_variable(  # var=var(time,lev,lat,lon)
                variableid=varid, filetable=filetable1, reduced_var_id=varid+'_1',
                reduction_function=(lambda x,vid: reduce_time_seasonal( x, self.season, vid ) ) ),
            'hyam': reduced_variable(   # hyam=hyam(lev)
                variableid='hyam', filetable=filetable1, reduced_var_id='hyam',
                reduction_function=(lambda x,vid=None: x) ),
            'hybm': reduced_variable(   # hybm=hybm(lev)
                variableid='hybm', filetable=filetable1, reduced_var_id='hybm',
                reduction_function=(lambda x,vid=None: x) ),
            'ps': reduced_variable(     # ps=ps(time,lat,lon)
                variableid='PS', filetable=filetable1, reduced_var_id='ps',
                reduction_function=(lambda x,vid=None: reduce_time_seasonal( x, self.season, vid ) ) )
            }
        vid1 = varid+'_p'+'_1'
        self.derived_variables = {
            vid1: derived_var( vid=vid1, inputs=[ varid+'_1', 'hyam', 'hybm', 'ps' ], func=verticalize )
            }
        pselect = udunits(200,'mbar')
        self.single_plotspecs = {
            self.plot1_id: plotspec(
                vid = varid+'_1',
                zvars = [vid1],  zfunc = (lambda z: select_lev( z, pselect ) ),
                plottype = self.plottype )
            }
        self.composite_plotspecs = {
            self.plotall_id: [ self.plot1_id ]            
            }
        self.computation_planned = True
    def _results(self):
        results = plot_spec._results(self)
        if results is None: return None
        return self.plotspec_values[self.plotall_id]