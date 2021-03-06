#!/usr/local/uvcdat/1.3.1/bin/python

# Functions callable from the UV-CDAT GUI.

import hashlib, os, pickle, sys, os, math
from metrics import *
from metrics.fileio.filetable import *
from metrics.fileio.findfiles import *
from metrics.computation.reductions import *
from metrics.amwg import *
from metrics.amwg.derivations.vertical import *
from metrics.amwg.plot_data import plotspec, derived_var
from metrics.common.version import version
from metrics.amwg.derivations import *
from metrics.diagnostic_groups import *
from pprint import pprint
import cProfile
import logging
import json
import vcs
vcsx=vcs.init()   # This belongs in one of the GUI files, e.g.diagnosticsDockWidget.py
                  # The GUI probably will have already called vcs.init().
                  # Then, here,  'from foo.bar import vcsx'
# ---------------- code to compute plot in another process, not specific to UV-CDAT:


from multiprocessing import Process, Semaphore, Pipe
import time
import cdms2

def _plotdata_run( child_conn, sema, plotspec, filetable1, filetable2, varname, seasonname, outputPath, unique_ID, aux=None, newgrid=0 ):
    #def _plotdata_run(plotspec, filetable1, filetable2, varname, seasonname, outputPath, unique_ID, aux=None ):
    global vcsx
    vcsx = False # temporary kludge
    sema.acquire()
    ps = plotspec( filetable1, filetable2, varname, seasonname, aux )
    if ps is None:
        results = None
        return results
    else:
        results = ps.compute(newgrid)
        outfile=os.path.join(outputPath,str(unique_ID))
        if type(results) is list:
            results_obj = uvc_composite_plotspec(results)
        else:
            results_obj = results
        results_obj.write_plot_data( "", outfile ) # second arg sdb directory
    sema.release()
    child_conn.send(outfile)
    return outfile

def plotdata_run( plotspec, filetable1, filetable2, varname, seasonname, outputPath, unique_ID, aux=None, newgrid=0 ):
    """Inputs:
    plotspec is a plot_spec class to be instantiated
    filetable1 is the model data file table
    fileteable2 is the obs or reference model data file table
    varname is a string representing the variable to be plotted
    seasonname is a string representing the season for climatology to be presented
    aux is an auxiliary option, if any

    This function will spawn another process and return it as p, an instance of
    multiprocessing.Process.  This p will create a plotspec object and run its compute() method.
    To check the status of p, call plotdata_status(p) to get a semaphore value (>0 means done).
    To get the computed value, call plotdata_results(p).
    """
    #logging.basicConfig(filename="diags.log",level=logging.INFO)
    #log = logging.getLogger("diags")
    sema = Semaphore()
    #log.info("initial sema=%s"%sema)
    parent_conn, child_conn = Pipe()
    p = Process( target=_plotdata_run,
                 args=(child_conn, sema,
                       plotspec, filetable1, filetable2, varname, seasonname, outputPath,
                       unique_ID, aux, newgrid ) )
    #log.info("initial p=%s"%(p))
    #outfile=_plotdata_run(plotspec, filetable1, filetable2, varname, seasonname, outputPath,
    #                      unique_ID, aux, newgrid)
    #print outfile
    """
    p = Process( target=_plotdata_run,
                 args=( plotspec, filetable1, filetable2, varname, seasonname, outputPath,
                        unique_ID, aux, newgrid ) )
    """
    p.start()
    p.sema = sema
    #pid = p.pid
    #p.join()
    p.parent_conn = parent_conn
    return p

def plotdata_status( p ):
    # Returns True if a process is running to compute diagnostics; False otherwise.
    #log = logging.getLogger("diags")
    sema = p.sema
    acq = p.sema.acquire( block=False )  # returns immediately
    if acq:
        # We've acquired the semaphore, which means the assiciated process isn't running.
        sema.release()
        return False
    else:
        # We can't acquire the semaphore, which means the assiciated process is running.
        return True

def plotdata_results( p ):
    results = p.parent_conn.recv()
    p.join()  # assumption: the process won't be needed after we have the results
    return results

# ----------------

def setup_filetable( search_path, cache_path, ftid=None, search_filter=None ):
    print "jfp in setup_filetable, search_path=",search_path," search_filter=",search_filter
    #try:
    datafiles = dirtree_datafiles( search_path, search_filter )
    return datafiles.setup_filetable( cache_path, ftid )
    #except Exception, err:
    #    print "=== EXCEPTION in setup_filetable ===", err
    #    return None

def clear_filetable( search_path, cache_path, search_filter=None ):
    """obsolete; Deletes (clears) the cached file table created by the corresponding call of setup_filetable"""
    search_path = os.path.abspath(search_path)
    cache_path = os.path.abspath(cache_path)
    csum = hashlib.md5(search_path+cache_path).hexdigest()  #later will have to add search_filter
    cachefilename = csum+'.cache'
    cachefile=os.path.normpath( cache_path+'/'+cachefilename )

    if os.path.isfile(cache_path):
        os.remove(cache_path)

class uvc_composite_plotspec():
    def __init__( self, uvcps ):
        """uvcps is a list of instances of uvc_simple_plotspec"""
        ups = [p for p in uvcps if p is not None]
        self.plots = ups
        self.title = ' '.join([p.title for p in ups])
    def finalize( self ):
        for p in self.plots:
            p.finalize()
    def outfile( self, format='xml-NetCDF', where=""):
        print "jfp self.title=",self.title
        if len(self.title)<=0:
            fname = 'foo.xml'
        else:
            fname = (self.title.strip()+'.xml').replace(' ','_')[:115]  # 115 is to constrain file size
            fname = fname+'.xml'
        filename = os.path.join(where,fname)
        print "output to",filename
        return filename
    def write_plot_data( self, format="", where="" ):
        if format=="" or format=="xml" or format=="xml-NetCDF" or format=="xml file":
            format = "xml-NetCDF"
            contents_format = "NetCDF"
        else:
            print "WARNING: write_plot_data cannot recognize format name",format,\
                ", will write a xml file pointing to NetCDF files."
            format = "xml-NetCDF"
            conents_format = "NetCDF"

        for p in self.plots:
            p.write_plot_data( contents_format, where )

        print "jfp format=",format
        print "jfp where=",where
        filename = self.outfile( format, where )
        print "jfp filename=",filename
        writer = open( filename, 'w' )    # later, choose a better name and a path!
        writer.write("<plotdata>\n")
        for p in self.plots:
            pfn = p.outfile(where)
            writer.write( "<ncfile>"+pfn+"</ncfile>\n" )
        writer.write( "</plotdata>\n" )
        writer.close()

class uvc_simple_plotspec():
    """This is a simplified version of the plotspec class, intended for the UV-CDAT GUI.
    Once it stabilizes, I may replace the plotspec class with this one.
    The plots will be of the type specified by presentation.  The data will be the
    variable(s) supplied, and their axes.  Optionally one may specify a list of labels
    for the variables, and a title for the whole plot."""
    # re prsentation (plottype): Yxvsx is a line plot, for Y=Y(X).  It can have one or several lines.
    # Isofill is a contour plot.  To make it polar, set projection=polar.  I'll
    # probably communicate that by passing a name "Isofill_polar".
    def __init__( self, pvars, presentation, labels=[], title=''):
        ptype = presentation
        if vcsx:   # temporary kludge, presently need to know whether preparing VCS plots
            if presentation=="Yxvsx":
                self.presentation = vcsx.createyxvsx()
                ptype="Yxvsx"
            elif presentation == "Isofill":
                self.presentation = vcsx.createisofill()
            elif presentation == "Vector":
                self.presentation = vcsx.createvector()
            elif presentation == "Boxfill":
                self.presentation = vcsx.createboxfill()
            elif presentation == "Isoline":
                self.presentation = vcsx.createisoline()
            else:
                print "ERROR, uvc_plotspec doesn't recognize presentation",presentation
                self.presentation = "Isofill"  # try to go on
        else:
            self.presentation = presentation
        ## elif presentation == "":
        ##     self.resentation = vcsx.create
        self.vars = pvars
        self.labels = labels
        self.title = title
        self.type = ptype
        self.ptype = ptype
        # Initial ranges - may later be changed to coordinate with related plots:
        # For each variable named 'v', the i-th member of self.vars, (most often there is just one),
        # varmax[v] is the maximum value of v, varmin[v] is the minimum value of v,
        # axmax[v][ax] is the maximum value of the axis of v with id=ax.
        # axmin[v][ax] is the minimum value of the axis of v with id=ax.
        self.varmax = {}
        self.varmin = {}
        self.axmax = {}
        self.axmin = {}
        self.axax = {}
        for var in pvars:
            self.varmax[var.id] = var.max()
            self.varmin[var.id] = var.min()
            self.axmax[var.id]  = { ax[0].id:max(ax[0][:]) for ax in var._TransientVariable__domain[:]
                                    if ax is not None }
            self.axmin[var.id]  = { ax[0].id:min(ax[0][:]) for ax in var._TransientVariable__domain[:]
                                    if ax is not None}
            self.axax[var.id]  = { ax[0].id:ax[0].axis for ax in var._TransientVariable__domain[:]
                                   if ax is not None}
        self.finalized = False

    def finalize( self ):
        """By the time this is called, all synchronize operations should have been done.  But even
        so, each variable has a min and max and a min and max for each of its axes.  We need to
        simplify further for the plot package."""
        if self.presentation.__class__.__name__=="GYx" or\
                self.presentation.__class__.__name__=="Gfi":
            var = self.vars[0]
            axmax = self.axmax[var.id]
            axmin = self.axmin[var.id]
            varmax = self.varmax[var.id]
            varmin = self.varmin[var.id]
            for v in self.vars[1:]:
                for ax in axmax.keys():
                    axmax[ax] = max(axmax[ax],self.axmax[v.id][ax])
                    axmin[ax] = min(axmin[ax],self.axmin[v.id][ax])
                varmax = max(varmax,self.varmax[v.id])
                varmin = min(varmin,self.varmin[v.id])
            if self.presentation.__class__.__name__=="GYx":
                # VCS Yxvsx
                ax = axmax.keys()[0]
                self.presentation.datawc_x1 = axmin[ax]
                self.presentation.datawc_x2 = axmax[ax]
                self.presentation.datawc_y1 = varmin
                self.presentation.datawc_y2 = varmax
            elif self.presentation.__class__.__name__=="Gfi":
                # VCS Isofill
                # First we have to identify which axes will be plotted as X and Y.
                # The following won't cover all cases, but does cover what we have:
                axaxi = {ax:id for id,ax in self.axax[var.id].items()}
                if 'X' in axaxi.keys():
                    axx = axaxi['X']
                    axy = axaxi['Y']
                else:
                    axx = axaxi['Y']
                    axy = axaxi['Z']
                # Now send the plotted min,max for the X,Y axes to the graphics:
                self.presentation.datawc_x1 = axmin[axx]
                self.presentation.datawc_x2 = axmax[axx]
                self.presentation.datawc_y1 = axmin[axy]
                self.presentation.datawc_y2 = axmax[axy]
                # The variable min and max, varmin and varmax, should be passed on to the graphics
                # for setting the contours.  But apparently you can't tell VCS just the min and max;
                # you have to give it all the contour levels.  So...
                nlevels=10
                nlrange = range(nlevels+1)
                nlrange.reverse()
                vminl = varmin/nlevels
                vmaxl = varmax/nlevels
                levels = [a*vminl+(nlevels-a)*vmaxl for a in nlrange]
                levels[0] = math.floor(levels[0])  # could do better but too much trouble
                levels[-1] = math.ceil(levels[-1])
                self.presentation.levels = (levels,)
                # Once you set the levels, the VCS default color choice looks bad.  So you really
                # have to set contour fill colors (integers from 0 through 255) too:
                cmin = 32./nlevels
                cmax = 255./nlevels
                # A more flexible way to do what's going on here, thanks to Charles Doutriaux:
                # r=10
                # g=16
                # b=20
                # X.setcolorcell(16,r,g,b)
                # colors = [16,17,18,...] etc.
                # vcs.getcolors is useful, more complicated - see its doc string
                # vcs.mkscale probably does exactly what we need here - see its doc string
                colors =  [int(round(a*cmin+(nlevels-a)*cmax)) for a in nlrange]
                self.presentation.fillareacolors = colors
                #self.presentation.fillareacolors=[32,48,64,80,96,112,128,144,160,176,240]

    def __repr__(self):
        return ("uvc_plotspec %s: %s\n" % (self.presentation,self.title))
    def _json(self,*args,**kwargs):
        """returns a JSON serialization of this object"""
        vars_json_list = [ v.dumps() for v in self.vars ]
        vars_json = json.dumps(vars_json_list)
        return {'vars':vars_json, 'presentation':self.presentation, 'type':self.type,\
                    'labels':self.labels, 'title':self.title }
    def synchronize_ranges( self, pset ):
        """Synchronize the range attributes of this and another uvc_plotspec object, pset.
        That is, numerical values of corresponding range attributes will be changed to be the same.
        A problem is that these ranges are tied to variable names, and the variable names should be
        unique.  Typically the ranges we want to synchronize belong to the same variable from two
        filetables, so the variable names are of the form VAR_1 and VAR_2.  For the moment, we'll
        just strip off _1 and _2 endings, but in the future something more reliable will be needed,
        e.g. index dicts off a tuple such as ("VAR",2) instead of a string "VAR_2".
        """
        self.synchronize_values( pset )
        self.synchronize_axes(pset)
    def synchronize_values( self, pset, suffix_length=2 ):
        "the part of synchronize_ranges for variable values only"
        sl = -suffix_length
        if sl==0:
            self_suffix = ""
            pset_suffix = ""
        else:
            self_suffix = self.vars[0].id[sl:]
            pset_suffix = pset.vars[0].id[sl:]
        if sl==0:
            var_ids = set([v.id for v in self.vars]) & set([v.id for v in pset.vars])
        else:
            var_ids = set([v.id[:sl] for v in self.vars]) & set([v.id[:sl] for v in pset.vars])
        for vid in var_ids:
            vids = vid+self_suffix
            vidp = vid+pset_suffix
            print "jfp vid,vids,vidp=",vid,vids,vidp
            varmax = max( self.varmax[vids], pset.varmax[vidp] )
            varmin = min( self.varmin[vids], pset.varmin[vidp] )
            self.varmax[vids] = varmax
            pset.varmax[vidp] = varmax
            self.varmin[vids] = varmin
            pset.varmin[vidp] = varmin
    def synchronize_many_values( self, psets, suffix_length=0 ):
        """the part of synchronize_ranges for variable values only - except that psets is a list of
        uvc_plotset instances.  Thus we can combine ranges of many variable values."""
        sl = -suffix_length
        if sl==0:
            self_suffix = ""
        else:
            self_suffix = self.vars[0].id[sl:]
        pset_suffices = range(len(psets))
        for i in range(len(psets)):
            if sl==0:
                pset_suffices[i] = ""
            else:
                pset_suffices[i] = psets[i].vars[0].id[sl:]
        if sl==0:
            var_ids = set([v.id for v in self.vars])
            for i in range(len(psets)):
                var_ids =  var_ids & set([v.id for v in psets[i].vars])
        else:
            var_ids = set([v.id[:sl] for v in self.vars])
            for i in range(len(psets)):
                var_ids = var_ids & set([v.id[:sl] for v in psets[i].vars])
        for vid in var_ids:
            vids = vid+self_suffix
            varmax = self.varmax[vids]
            varmin = self.varmin[vids]
            for i in range(len(psets)):
                vidp = vid+pset_suffices[i]
                print "jfp vid,vids,vidp=",vid,vids,vidp
                varmax = max( varmax, psets[i].varmax[vidp] )
                varmin = min( varmin, psets[i].varmin[vidp] )
            self.varmax[vids] = varmax
            self.varmin[vids] = varmin
            for i in range(len(psets)):
                vidp = vid+pset_suffices[i]
                psets[i].varmax[vidp] = varmax
                psets[i].varmin[vidp] = varmin
    def synchronize_axes( self, pset ):
        "the part of synchronize_ranges for axes only"
        self_suffix = self.vars[0].id[-2:]
        pset_suffix = pset.vars[0].id[-2:]
        var_ids = set([v.id[:-2] for v in self.vars]) & set([v.id[:-2] for v in pset.vars])
        vards = { v.id: v for v in self.vars }
        vardp = { v.id: v for v in pset.vars }
        for vid in var_ids:
            vids = vid+self_suffix
            vidp = vid+pset_suffix
            ax_ids = set([ ax[0].id for ax in vards[vids]._TransientVariable__domain ]) & \
                set([ ax[0].id for ax in vardp[vidp]._TransientVariable__domain ])
            axmaxs = { aid: max( self.axmax[vids][aid], pset.axmax[vidp][aid] ) for aid in ax_ids }
            axmins = { aid: min( self.axmin[vids][aid], pset.axmin[vidp][aid] ) for aid in ax_ids }
            for aid in ax_ids:
                self.axmax[vids][aid] = axmaxs[aid]
                pset.axmax[vidp][aid] = axmaxs[aid]
                self.axmin[vids][aid] = axmins[aid]
                pset.axmin[vidp][aid] = axmins[aid]
        
    def outfile( self, format="", where="" ):
        if len(self.title)<=0:
            fname = 'foo'
        else:
            fname = (self.title.strip()+'.nc').replace(' ','_')
        filename = os.path.join(where,fname)
        print "output to",filename
        return filename
    def write_plot_data( self, format="", where="" ):
        # This is just experimental code, so far.
        if format=="" or format=="NetCDF" or format=="NetCDF file":
            format = "NetCDF file"
        elif format=="JSON string":
            pass
        elif format=="JSON file":
            pass
        else:
            print "WARNING: write_plot_data cannot recognize format name",format,\
                ", will write a NetCDF file."
            format = "NetCDF file"

        filename = self.outfile( format, where )

        if format=="NetCDF file":
            writer = cdms2.open( filename, 'w' )    # later, choose a better name and a path!
        elif format=="JSON file":
            print "ERROR: JSON file not implemented yet"
        elif format=="JSON string":
            return json.dumps(self,cls=DiagsEncoder)

        writer.presentation = self.ptype
        plot_these = []
        for zax in self.vars:
            print "jfp zax.id=",zax.id
            writer.write( zax )
            plot_these.append( zax.id )
        writer.plot_these = ' '.join(plot_these)
        # Once the finalized method guarantees that varmax,varmin are numbers...
        #if self.finalized==True:
        #    writer.varmax = self.varmax
        #    writer.varmin = self.varmin

        writer.close()

class uvc_plotspec(uvc_simple_plotspec):
    pass

class uvc_zero_plotspec(uvc_simple_plotspec):
    # for convenience in clearing a cell in the UV-CDAT GUI
    def __init__( self ):
        zerovar = cdms2.createVariable([[0,0,0],[0,0,0]])
        zerovar.id = 'zero'
        uvc_simple_plotspec.__init__( self, [zerovar], "Isofill" )

class DiagsEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj._json()

def get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """returns a list of uvc_plotspec objects to be plotted.  The plot_set is a string from
    1,2,3,4,4a,5,...,16.  Usually filetable1 indexes model data and filetable2 obs data,  but
    anything generated by setup_filetable() is ok.  The variable is a string - it can be a data
    variable from the indexed data sets, or a derived variable.  The season is a 3-letter code,
    e.g. 'DJF','ANN','MAR'.
    This is DEPRECATED and AMWG-specific.  It is better to call a method obtained by a call
    of the list_diagnostic_sets() method of BasicDiagnosticGroup and its children such as AMWG."""
    print "WARNING - deprecated function get_plot_data() has been called."
    return _get_plot_data( plot_set, filetable1, filetable2, variable, season)

# To profile, replace (by name changes) the above get_plot_data() with the following one:
def profiled_get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """returns a list of uvc_plotspec objects to be plotted.  The plot_set is a string from
    1,2,3,4,4a,5,...,16.  Usually filetable1 indexes model data and filetable2 obs data,  but
    anything generated by setup_filetable() is ok.  The variable is a string - it can be a data
    variable from the indexed data sets, or a derived variable.  The season is a 3-letter code,
    e.g. 'DJF','ANN','MAR'."""
    args = [ plot_set, filetable1, filetable2, variable, season ]
    prof = cProfile.Profile()
    returnme = prof.runcall( _get_plot_data, *args )
    prof.print_stats()   # use dump_stats(filename) to print to file
    return returnme

def _get_plot_data( plot_set_id, filetable1, filetable2, variable, season ):
    """the real _get_plot_data() function; get_plot_data() is a simple wrapper around this"""
    if season=='ANN':
        # cdutil.times.getMonthIndex() (called by climatology()) doesn't recognize 'ANN'
        season='JFMAMJJASOND'
    plot_set_id = plot_set_id.strip()
    from metrics.amwg.amwg import plot_set2, plot_set3, plot_set4, plot_set5
    if plot_set_id=='2':
        return plot_set2( filetable1, filetable2, variable )
    if plot_set_id=='3':
        return plot_set3( filetable1, filetable2, variable, season )
    elif plot_set_id=='4':
        return plot_set4( filetable1, filetable2, variable, season )
    elif plot_set_id=='5':
        return plot_set5( filetable1, filetable2, variable, season )
    else:
        print "ERROR, plot set",plot_set_id," not implemented yet!"
        return None
    

class basic_one_line_plot( plotspec ):
    def __init__( self, yvar, xvar=None ):
        # xvar, yvar should be the actual x,y of the plot.
        # xvar, yvar should already have been reduced to 1-D variables.
        # Normally y=y(x), x is the axis of y.
        if xvar is None:
            xvar = yvar.getAxisList()[0]
        if xvar == "never really come here":
            ### modified sample from Charles of how we will pass around plot parameters...
            vcsx = vcs.init()      # but note that this doesn't belong here!
            yx=vcsx.createyxvsx()
            # Set the default parameters
            yx.datawc_y1=-2  # a lower bound, "data 1st world coordinate on Y axis"
            yx.datawc_y2=4  # an upper bound, "data 2nd world coordinate on Y axis"
            plotspec.__init__( self, xvars=[xvar], yvars=[yvar],
                               vid = yvar.id+" line plot", plottype=yx.tojson() )
            ### ...sample from Charles of how we will pass around plot parameters
        else:
            # This is the real code:
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
    def compute(self,newgrid=0):
        return self.results(newgrid)
    def results(self,newgrid=0):
        return self._results(newgrid)
# To profile, replace (by name changes) the above results() with the following one:
    def profiled_results(self,newgrid=0):
        if newgrid!=0:
            print "ERROR haven't implemented profiling with argument"
        prof = cProfile.Profile()
        returnme = prof.runcall( self._results )
        prof.dump_stats('results_stats')
        return returnme
    def _results(self, newgrid=0 ):
        """newgrid=0 for keep original. !=0 to use any regridded variants of variables - presently
        that means a coarser grid, typically from regridding model data to the obs grid.
        In the future regrid>0 will mean regrid everything to the finest grid and regrid<0
        will mean regrid everything to the coarsest grid."""
        for v in self.reduced_variables.keys():
            value = self.reduced_variables[v].reduce()
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
            print "jfp preparing data for",ps._id
            try:
                xrv = [ varvals[k] for k in ps.xvars ]
                x1rv = [ varvals[k] for k in ps.x1vars ]
                x2rv = [ varvals[k] for k in ps.x2vars ]
                x3rv = [ varvals[k] for k in ps.x3vars ]
                yrv = [ varvals[k] for k in ps.yvars ]
                y1rv = [ varvals[k] for k in ps.y1vars]
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
            except Exception as e:
                print "cannot compute data for",ps._id
                self.plotspec_values[p] = None
                continue
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
                if hasattr(zax,'regridded') and newgrid!=0:
                    vars.append( regridded_vars[zax.regridded] )
                else:
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
    
