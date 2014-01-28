#!/usr/local/uvcdat/1.3.1/bin/python

# This is meant to be the genericized version of uvcdat.py.
# There were too many interdependancies to cleanly seperate the UVCDAT parts from the generic parts
# so this is a reworking of the generic parts.

from metrics.computation.reductions import *
from metrics.computation.plotspec import *
# this whole system is questionable. we really should be able to import a top level directory
# otherwise there are dozens of places this code needs updated...
# plus we have duplicate name/symbols

from metrics.frontend.version import version
from metrics.frontend.options import Options
from metrics.packages.amwg.derivations import *
from metrics.packages.common.diagnostic_groups import *
import metrics.packages

from pprint import pprint
import vcs



# TODO: This should not be inside uvcdat.py. It is general purpose. Probably needs
# moved to packages/common or something similar
class plot_spec(object):
    # ...I made this a new-style class so we can call __subclasses__ .
    package=BasicDiagnosticGroup  # Note that this is a class not an object.
    def __repr__( self ):
        if hasattr( self, 'plotall_id' ):
            return self.__class__.__name__+'('+self.plotall_id+')'
        else:
            return self.__class__.__name__+' object'
    def __init__(self, seasonid='ANN', *args ):
        self._season_displayid = seasonid
        if seasonid=='ANN' or seasonid is None:
            # cdutil.times.getMonthIndex() (called by climatology()) doesn't recognize 'ANN'
            self._seasonid='JFMAMJJASOND'
        else:
            self._seasonid=seasonid
        self.reduced_variables = {}
        self.derived_variables = {}
        self.variable_values = {}
        self.single_plotspecs = {}
        self.composite_plotspecs = {}
        self.plotspec_values = {}
        self.computation_planned = False
    def plan_computation( self, seasonid):
        pass
    def _build_label( self, vars, p ):
        yls = []
        for y in vars:
            if type(y) is tuple:
                yl = getattr(y[0],'_vid',None)
            else:
                yl = getattr(y,'_vid',None)
            if yl is not None:
                yls.append( yl )
        new_id = '_'.join(yls)
        if new_id is None or new_id.strip()=="": new_id = p+'_2'
        return new_id
    def compute(self):
        return self.results()
    def results(self):
        return self._results()
# To profile, replace (by name changes) the above results() with the following one:
    def profiled_results(self):
        prof = cProfile.Profile()
        returnme = prof.runcall( self._results )
        prof.dump_stats('results_stats')
        return returnme
    def _results(self):
        opts = Options()
        opts._opts['vars'] = self.reduced_variables.keys()
        for v in self.reduced_variables.keys():
            value = self.reduced_variables[v].reduce(opts)
            self.variable_values[v] = value  # could be None
        postponed = []   # derived variables we won't do right away
        for v in self.derived_variables.keys():
            value = self.derived_variables[v].derive(self.variable_values)
            if value is None:
                # couldn't compute v - probably it depends on another derived variables which
                # hasn't been computed yet
                postponed.append(v)
            else:
                self.variable_values[v] = value
        for v in postponed:   # Finish up with derived variables
            value = self.derived_variables[v].derive(self.variable_values)
            self.variable_values[v] = value  # could be None
        varvals = self.variable_values
        for p,ps in self.single_plotspecs.iteritems():
            print "frontend - jfp preparing data for",ps._id
            xrv = [ varvals[k] for k in ps.xvars ]
            x1rv = [ varvals[k] for k in ps.x1vars ]
            x2rv = [ varvals[k] for k in ps.x2vars ]
            x3rv = [ varvals[k] for k in ps.x3vars ]
            yrv = [ varvals[k] for k in ps.yvars ]
            y1rv = [ varvals[k] for k in ps.y1vars ]
            y2rv = [ varvals[k] for k in ps.y2vars ]
            y3rv = [ varvals[k] for k in ps.y3vars ]
            yarv = [ varvals[k] for k in ps.yavars ]
            ya1rv = [ varvals[k] for k in ps.ya1vars ]
            zrv = [ varvals[k] for k in ps.zvars ]
            zrrv = [ varvals[k] for k in ps.zrangevars ]
            xax = apply( ps.xfunc, xrv )
            x1ax = apply( ps.x1func, x1rv )
            x2ax = apply( ps.x2func, x2rv )
            x3ax = apply( ps.x3func, x3rv )
            yax = apply( ps.yfunc, yrv )
            y1ax = apply( ps.y1func, y1rv )
            y2ax = apply( ps.y2func, y2rv )
            y3ax = apply( ps.y3func, y3rv )
            # not used yet yaax = apply( ps.yafunc, yarv )
            ya1ax = apply( ps.ya1func, ya1rv )
            zax = apply( ps.zfunc, zrv )
            # not used yet zr = apply( ps.zrangefunc, zrrv )
            vars = []
            # The x or x,y vars will hopefully appear as axes of the y or z
            # vars.  This needs more work; but for now we never want x vars here:
            xlab=""
            ylab=""
            zlab=""
            if xax is not None:
                xlab += ' '+xax.id
            if x1ax is not None:
                xlab += ' '+x1ax.id
            if x2ax is not None:
                xlab += ', '+x2ax.id
            if x3ax is not None:
                xlab += ', '+x3ax.id
            if yax is not None:
                vars.append( yax )
                new_id = self._build_label( yrv, p )
                yax.id = new_id
                ylab += ' '+yax.id
            if y1ax is not None:
                vars.append( y1ax )
                new_id = self._build_label( y1rv, p )
                y1ax.id = new_id
                ylab += ' '+y1ax.id
            if y2ax is not None:
                vars.append( y2ax )
                new_id = self._build_label( y2rv, p )
                y2ax.id = new_id
                ylab += ', '+y2ax.id
            if y3ax is not None:
                vars.append( y3ax )
                new_id = self._build_label( y3rv, p )
                y3ax.id = new_id
                ylab += ', '+y3ax.id
            if zax is not None:
                vars.append( zax )
                new_id = self._build_label( zrv, p )
                zax.id = new_id
                zlab += ' '+zax.id
            if vars==[]:
                self.plotspec_values[p] = None
                continue
            labels = [xlab,ylab,zlab]
            title = ' '.join(labels)+' '+self._season_displayid  # do this better later
            self.plotspec_values[p] = uvc_plotspec( vars, self.plottype, labels, title )
        for p,ps in self.composite_plotspecs.iteritems():
            self.plotspec_values[p] = [ self.plotspec_values[sp] for sp in ps ]

        return self
        
class basic_plot_variable():
    """represents a variable to be plotted.  This need not be an actual data variable;
       it could be some derived quantity"""
    def __init__( self, name, plotset_name, package ):
        self.name = name
        self.plotset_name = plotset_name
        self.package = package
    @staticmethod
    def varoptions(*args,**kwargs):
        """returns a represention of options specific to this variable.  Example dict items:
         'vertical average':'vertavg'
         '300 mbar level value':300
        """
        return None
    
class basic_level_variable(basic_plot_variable):
    """represents a typical variable with a level axis, in a plot set which reduces the level
    axis."""
    @staticmethod
    def varoptions():
        """returns a represention of options specific to this variable.  That is, how should
        one reduce the level axis?  The default is to average along that axis.  But other options
        are to pick out the variable's value at some particular pressure level, e.g. 300 mb.
        """
        opts ={
            " default":"vertical average", " vertical average":"vertical average",
            "200 mbar":200, "300 mbar":300, "500 mbar":500, "850 mbar":850 }
        return opts
    
class basic_one_line_plot( plotspec ):
    def __init__( self, yvar, xvar=None ):
        # xvar, yvar should be the actual x,y of the plot.
        # xvar, yvar should already have been reduced to 1-D variables.
        # Normally y=y(x), x is the axis of y.
        if xvar is None:
            xvar = yvar.getAxisList()[0]
        plotspec.__init__( self, xvars=[xvar], yvars=[yvar],
                           vid = yvar.id+" line plot", plottype='Yxvsx' )

class basic_two_line_plot( plotspec ):
    def __init__( self, y1var, y2var, x1var=None, x2var=None ):
        """x?var, y?var should be the actual x,y of the plots.
        x?var, y?var should already have been reduced to 1-D variables.
        Normally y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self, y1vars=[y1var], y2vars=[y2var],
                           vid = y1var.variableid+y2var.variableid+" line plot", plottype='Yxvsx' )

class one_line_diff_plot( plotspec ):
    def __init__( self, y1var, y2var, vid ):
        """y?var should be the actual y of the plots.
        y?var should already have been reduced to 1-D variables.
        y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self,
            xvars=[y1var,y2var], xfunc = latvar_min,
            yvars=[y1var,y2var],
            yfunc=aminusb_1ax,   # aminusb_1ax(y1,y2)=y1-y2; each y has 1 axis, use min axis
            vid=vid,
            plottype='Yxvsx' )

class contour_plot( plotspec ):
    def __init__( self, zvar, xvar=None, yvar=None, ya1var=None,
                  xfunc=None, yfunc=None, ya1func=None ):
        """ zvar is the variable to be plotted.  xvar,yvar are the x,y of the plot,
        normally the axes of zvar.  If you don't specify, a x=lon,y=lat plot will be preferred.
        xvar, yvar, zvar should already have been reduced; x,y to 1-D and z to 2-D."""
        if xvar is None:
            xvar = zvar
        if yvar is None:
            yvar = zvar
        if ya1var is None:
            ya1var = zvar
        if xfunc==None: xfunc=lonvar
        if yfunc==None: yfunc=latvar
        vid = ''
        if hasattr(zvar,'vid'): vid = zvar.vid
        if hasattr(zvar,'id'): vid = zvar.id
        plotspec.__init__(
            self, vid+'_contour', xvars=[xvar], xfunc=xfunc,
            yvars=[yvar], yfunc=yfunc, ya1vars=[ya1var], ya1func=ya1func,
            zvars=[zvar], plottype='Isofill' )

class contour_diff_plot( plotspec ):
    def __init__( self, z1var, z2var, plotid, x1var=None, x2var=None, y1var=None, y2var=None,
                   ya1var=None,  ya2var=None, xfunc=None, yfunc=None, ya1func=None ):
        """We will plot the difference of the two z variables, z1var-z2var.
        See the notes on contour_plot"""
        if x1var is None:
            x1var = z1var
        if y1var is None:
            y1var = z1var
        if ya1var is None:
            ya1var = z1var
        if x2var is None:
            x2var = z2var
        if y2var is None:
            y2var = z2var
        if ya2var is None:
            ya2var = z2var
        if xfunc==None: xfunc=lonvar_min
        if yfunc==None: yfunc=latvar_min
        plotspec.__init__(
            self, plotid, xvars=[x1var,x2var], xfunc=xfunc,
            yvars=[y1var,y2var], yfunc=yfunc, ya1vars=[ya1var,ya2var], ya1func=ya1func,
            zvars=[z1var,z2var], zfunc=aminusb_2ax, plottype='Isofill' )
