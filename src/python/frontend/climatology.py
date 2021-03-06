#!/usr/local/uvcdat/1.3.1/bin/python

# High-level functions to convert data to climatology files.
# These are, in my understanding, files which have a time-average of the original
# variables, with the time often restricted to a month or season.
# This is basically a simplified version of plot_data.py.

# TO DO >>>> run argument: dict of attribute:value to be written out as file global attributes.

import cdms2, math
from metrics.fileio.findfiles import *
from metrics.fileio.filetable import *
from metrics.computation.reductions import *
from metrics.amwg.derivations.oaht import *
from metrics.amwg.derivations.ncl_isms import *
from metrics.amwg.derivations.vertical import *
from metrics.amwg.plot_data import derived_var, plotspec
from cdutil.times import Seasons
from pprint import pprint
import cProfile

class climatology_variable( reduced_variable ):
    def __init__(self,varname,filetable,seasonname='ANN'):
        self.seasonname = seasonname
        if seasonname=='ANN':
            reduced_variable.__init__( self,
               variableid=varname, filetable=filetable,
               reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)) )
        else:
            season = cdutil.times.Seasons([seasonname])
            reduced_variable.__init__( self,
               variableid=varname, filetable=filetable,
               reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,season)) )

class climatology_squared_variable( reduced_variable ):
    """represents the climatology of the square of a variable.
    This, together with the variable's climatology, is theoretically sufficient for computing
    its variance; but it would be numerically better to use this as a model for a class
    representing the climatology of (var - climo(var))^2."""
    def __init__(self,varname,filetable,seasonname='ANN'):
        duv = derived_var( varname+'_sq', [varname], func=(lambda x: atimesb(x,x)) )
        self.seasonname = seasonname
        if seasonname=='ANN':
            reduced_variable.__init__(
                self,
                variableid=varname+'_sq', filetable=filetable,
                reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)),
                duvs={ varname+'_sq':duv }, rvs={} )
        else:
            season = cdutil.times.Seasons([seasonname])
            reduced_variable.__init__(
                self,
                variableid=varname+'_sq', filetable=filetable,
                reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,season)),
                duvs={ varname+'_sq':duv }, rvs={} )

class climatology_variance( reduced_variable ):
    """represents a variance - the climatology of (v-climo(v))^2 where v is a variable.
    Note that we're computing the variance on all data, not a sample - so the implicit
    1/N in the average (not 1/(N-1)) is correct."""
    def __init__(self,varname,filetable,seasonname='ANN',rvs={}):
        duv = derived_var( varname+'_var',
                           [varname,'_'.join([varname,seasonname])], func=varvari )
        self.seasonname = seasonname
        if seasonname=='ANN':
            reduced_variable.__init__(
                self,
                variableid=varname+'_var', filetable=filetable,
                reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)),
                duvs={ varname+'_var':duv }, rvs=rvs )
        else:
            season = cdutil.times.Seasons([seasonname])
            reduced_variable.__init__(
                self,
                variableid=varname+'_var', filetable=filetable,
                reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,season)),
                duvs={ varname+'_var':duv }, rvs=rvs )

def compute_and_write_climatologies( varkeys, reduced_variables, season, case='', variant='' ):
    """Computes climatologies and writes them to a file.
    Inputs: varkeys, names of variables whose climatologies are to be computed
            reduced_variables, dict (key:rv) where key is a variable name and rv an instance
               of the class reduced_variable
            season: the season on which the climatologies will be computed
            variant: a string to be inserted in the filename"""
    # Compute the value of every variable we need.
    varvals = {}
    # First compute all the reduced variables
    # Probably this loop consumes most of the running time.  It's what has to read in all the data.
    for key in varkeys:
        if key in reduced_variables:
            varvals[key] = reduced_variables[key].reduce()

    for key in varkeys:
        if key in reduced_variables:
            var = reduced_variables[key]
            if varvals[key] is not None:
                if 'case' in var._file_attributes.keys():
                    case = var._file_attributes['case']+'_'
                    break

    print "writing climatology file for",case,variant,season
    if variant!='':
        variant = variant+'_'
    filename = case + variant + season + "_climo.nc"
    # ...actually we want to write this to a full directory structure like
    #    root/institute/model/realm/run_name/season/
    g = cdms2.open( filename, 'w' )    # later, choose a better name and a path!
    for key in varkeys:
        if key in reduced_variables:
            var = reduced_variables[key]
            if varvals[key] is not None:
                varvals[key].id = var.variableid
                varvals[key].reduced_variable=varvals[key].id
                if hasattr(var,'units'):
                    varvals[key].units = var.units+'*'+var.units
                g.write(varvals[key])
                for attr,val in var._file_attributes.items():
                    if not hasattr( g, attr ):
                        setattr( g, attr, val )
    g.season = season
    g.close()
    return varvals,case

def test_driver( path1, filt1=None ):
    """ Test driver for setting up data for plots"""
    datafiles1 = dirtree_datafiles( path1, filt1 )
    get_them_all = True  # Set True to get all variables in all specified files
    # Then you can call filetable1.list_variables to get the variable list.
    #was filetable1 = basic_filetable( datafiles1, get_them_all )
    filetable1 = datafiles1.setup_filetable( os.path.join(os.environ['HOME'],'tmp'), "model" )
    cseasons = ['ANN','DJF','MAM','JJA','SON',
                'JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    #cseasons = ['ANN', 'DJF', 'JJA' ] 
    #cseasons = ['JAN']
    case = ''

    for season in cseasons:

        reduced_variables1 = { var+'_'+season:climatology_variable(var,filetable1,season)
                               for var in filetable1.list_variables() }
        # example:             for var in ['TREFHT','FLNT','SOILC']}
        #reduced_variables = {
        #    'TREFHT_ANN': reduced_variable(
        #        variableid='TREFHT', filetable=filetable1,
        #        reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)) ),
        #    'TREFHT_DJF': reduced_variable(
        #        variableid='TREFHT', filetable=filetable1,
        #        reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,seasonsDJF,vid=vid)) ),
        #    'TREFHT_MAR': reduced_variable(
        #        variableid='TREFHT', filetable=filetable1,
        #        reduction_function=(lambda x,vid=None:
        #                                reduce_time_seasonal(x,Seasons(['MAR']),vid=vid)) )
        #    }
        # Get the case name, used to compute the output file name.
        varkeys = reduced_variables1.keys()
        #varkeys = varkeys[0:2]  # quick version for testing

        rvs,case = compute_and_write_climatologies( varkeys, reduced_variables1, season, case )

        # Repeat for var**2.  Later I'll change this to (var-climo(var))**2/(N-1)
        # using the (still-in-memory) data in the dict reduced_variables.
        #print "jfp\ndoing sq..."
        #reduced_variables2 = { var+'_'+season:climatology_squared_variable(var,filetable1,season)
        #                       for var in filetable1.list_variables() }
        #compute_and_write_climatologies( varkeys, reduced_variables2, season, case, 'sq' )

        # Repeat for variance, climatology of (var-climo(var))**2/(N-1)
        # using the (still-in-memory) data in the dict reduced_variables.
        print "jfp\ndoing var..."
        reduced_variables3 = { var+'_'+season:
                                   climatology_variance(var,filetable1,season,rvs=rvs)
                               for var in filetable1.list_variables() }
        compute_and_write_climatologies( varkeys, reduced_variables3, season, case, 'var' )

if __name__ == '__main__':
   if len( sys.argv ) > 1:
      path1 = sys.argv[1]
      if len( sys.argv ) > 2 and sys.argv[2].find('--filt=')==0:  # need to use getopt to parse args
          filt1 = sys.argv[2][7:]
          #filt1="f_and(f_startswith('FLUT'),"+filt1+")"
          test_driver(path1,filt1)
      else:
          #prof = cProfile.Profile()
          #args = [path1]
          #returnme = prof.runcall( test_driver, *args )
          #prof.print_stats()   # use dump_stats(filename) to print to file
          test_driver(path1)
   else:
      print "usage: plot_data.py root"
