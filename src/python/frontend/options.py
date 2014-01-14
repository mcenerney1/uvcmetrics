import argparse

### TODO: Fix compress options (in init or whatever)
#### NEED A REGIONS selection probably and maybe list of regions?

import metrics.packages as packages



class Options():
   all_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
   all_seasons = ['DJF', 'MAM', 'JJA', 'SON']
   all_regions = ['North America', 'South America']

   def __init__(self):
      self._opts = {}
      self._opts['compress'] = False
      self._opts['seasonally'] = False
      self._opts['monthly'] = False
      self._opts['yearly'] = False
      self._opts['json'] = False
      self._opts['netcdf'] = False
      self._opts['climatologies'] = True
      self._opts['plots'] = True
      self._opts['precomputed'] = False
      self._opts['realm'] = None
      self._opts['packages'] = None
      self._opts['vars'] = ['ALL']
      self._opts['sets'] = None
      self._opts['years'] = None
      self._opts['reltime'] = None
      self._opts['bounds'] = None
      self._opts['dsnames'] = []
      self._opts['filter'] = None
      self._opts['times'] = []
      self._opts['path'] = []
      self._opts['obspath'] = []

      # Generate a unique list of available realm types
      self.realm_types = packages.all_realms
      self.all_packages = packages.all_packages

      self.all_sets = {}
      for m in self.realm_types:
         for p in self.all_packages[m]:
            self.all_sets[p] = {}
            for s in packages.__dict__[p].package_ids:
               self.all_sets[p][s] = packages.__dict__[p].package_sets[s]

#      print self.all_sets

   def listSeasons(self):
      return self.all_seasons;

   def listPlots(self, sets):
      return

   # These two functions pretty much require some sort of iterable data structure for sets/vars
   def listAllVariables(self, realm, key=None):
      return
      # List all vars given a realm. This might be complicated to implement
      # Used to speed up the tree-based diags viewer from ORNL
   def listAllSets(self, realm=None, package=None):
      # primarily intended to make a JSON file for the d3 tree diags
      # most of this code moved to TreeView. Do we still need this functionality?
      return

   def listSets(self, packageid, key=None):
      im = ".".join(['metrics', 'packages', packageid, packageid])
      print __name__
      print 'lmwg'
      if packageid == 'lmwg':
         pclass = getattr(__import__(im, fromlist=['LMWG']), 'LMWG')()
      elif packageid == 'amwg':
         pclass = getattr(__import__(im, fromlist=['AMWG']), 'AMWG')()
      diags = pclass.list_diagnostic_sets()
      keys = diags.keys()
      keys.sort()
      sets = {}
      for k in keys:
         fields = k.split()
         sets[fields[0]] = ' '.join(fields[2:])
      return sets

##      if key != None: # For a specific field in the sets list, ie, key=name for example returns names
##         kys = self.all_sets[package].keys()
##         # assume "setXX" where XX is a number and we want "10" after "9" not "1"
##         kys.sort(key=lambda x:int(filter(str.isdigit, x)))
##         klist = []
##         for k in kys:
##            klist.append(self.all_sets[package][k][key])
##         return klist
##      else:
##         l = list(self.all_sets[package].keys())
##         l.sort(key=lambda x:int(filter(str.isdigit, x)))
##         return l
#         return list(self.all_sets[package].keys()).sort(key=lambda x:int(x[3:]))
#         return self.all_sets[package].keys()
      #return self.all_sets[realm][package]

   def listVariables(self, package, setname):
      import metrics.fileio.filetable as ft
      import metrics.fileio.findfiles as fi
      dtree = fi.dirtree_datafiles(self)
      filetable = ft.basic_filetable(dtree, self)

      # this needs a filetable probably, or we just define the maximum list of variables somewhere
      im = ".".join(['metrics', 'packages', package[0], package[0]])
      if package[0] == 'lmwg':
         pclass = getattr(__import__(im, fromlist=['LMWG']), 'LMWG')()
      elif package[0]=='amwg':
         pclass = getattr(__import__(im, fromlist=['AMWG']), 'AMWG')()

      # assume we have a path provided

      slist = pclass.list_diagnostic_sets()
      keys = slist.keys()
      keys.sort()
      pset_name = None
      for k in keys:
         fields = k.split()
         if setname[0] == fields[0]:
            pset = slist[k](filetable, None, None, None, aux=None, vlist=1)
            pset_name = k

      if pset_name == None:
         print 'DIDNT FIND THE SET'
         quit()

      
      varlist = pset.varlist
      print 'VARLIST'
      print varlist
         
      return

   def listRealms(self):
      return self.all_realms

   def listPackages(self, realm):
      if type(realm) == list:
         plist = []
         for m in realm:
            plist.append(self.all_packages[m])
         return plist
      else:
         return self.all_packages[realm]

   def verifyOptions(self):

   # TODO Determine if path is a single file, e.g. a cdscan generated XML file or a directory
   # and if it is a directory, if there is already a .xml file, ignore it or not. Might
   # need an option for that ignore option?
      if(self._opts['path'] == []):
         if(self._opts['list'] == None):
            print 'One or more path arguements is required'
            quit()
            
      if(self._opts['plots'] == True):
         if(self._opts['realm'] == None):
            print 'Please specify a realm type if you want to generate plots'
            quit()
         if(self._opts['packages'] == None):
            print 'Please specify a package name if you want to generate plots'
            quit()
         if(self._opts['sets'] == None):
            print 'Please specify set names if you want to generate plots'
            quit()
         # These could probably be assumed instead? 
         if(self._opts['realm'] != None):
            if(self._opts['packages'] == None):
               print 'Please specify a package name'
               quit()
            if(self._opts['sets'] == None):
               print 'Please specify a set name'
               quit()
         if(self._opts['packages'] != None):
            if(self._opts['sets'] == None):
               print 'Please specify a set name'
               quit()

   def processCmdLine(self):
      parser = argparse.ArgumentParser(
         description='UV-CDAT Climate Modeling Diagnostics', 
         usage='%(prog)s --path1 [--path2] [options]')

      parser.add_argument('--path', '-p', action='append', nargs=1, 
         help="Path to dataset(s). At least one path is required.")
      parser.add_argument('--obspath', action='append', nargs=1,
         help="Path to an observational dataset")
      parser.add_argument('--realm', '-r', nargs=1, choices=self.realm_types,
         help="The realm type. Current valid options are 'land' and 'atmosphere'")
      parser.add_argument('--filter', '-f', nargs=1, 
         help="A filespec filter. This will be applied to the dataset path(s) to narrow down file choices.")
      parser.add_argument('--packages', '--package', '-k', nargs='+', 
         help="The diagnostic packages to run against the dataset(s). Multiple packages can be specified.")
      parser.add_argument('--sets', '--set', '-s', nargs='+', 
         help="The sets within a diagnostic package to run. Multiple sets can be specified. If multiple packages were specified, the sets specified will be searched for in each package") 
      parser.add_argument('--vars', '--var', '-v', nargs='+', 
         help="Specify variables of interest to process. The default is all variables which can also be specified with the keyword ALL") 
      parser.add_argument('--list', '-l', nargs=1, choices=['sets', 'vars', 'variables', 'packages', 'realms', 'seasons', 'plottypes', 'allsets', 'allvariables'], 
         help="Determine which realms, packages, sets, and variables are available")
         # maybe eventually add compression level too....
      parser.add_argument('--compress', nargs=1, choices=['no', 'yes'],
         help="Turn off netCDF compression. This can be required for other utilities to be able to process the output files (e.g. parallel netCDF based tools") #no compression, add self state
      parser.add_argument('--output', '-o', nargs=1, 
         help="Specify an output base name. Typically, seasonal information will get postpended to this. For example -o myout will generate myout-JAN.nc, myout-FEB.nc, etc")
      parser.add_argument('--seasons', nargs='+', choices=self.all_seasons,
         help="Specify which seasons to generate climatoogies for")
      parser.add_argument('--years', nargs='+',
         help="Specify which years to include when generating climatologies") 
      parser.add_argument('--months', nargs='+', choices=self.all_months,
         help="Specify which months to generate climatologies for")
      parser.add_argument('--climatologies', '-c', nargs=1, choices=['no','yes'],
         help="Specifies whether or not climatologies should be generated")
      parser.add_argument('--plots', '-t', nargs=1, choices=['no','yes'],
         help="Specifies whether or not plots should be generated")
      parser.add_argument('--plottype', nargs=1)
      parser.add_argument('--precomputed', nargs=1, choices=['no','yes'], 
         help="Specifies whether standard climatologies are stored with the dataset (*-JAN.nc, *-FEB.nc, ... *-DJF.nc, *-year0.nc, etc")
      parser.add_argument('--json', '-j', nargs=1, choices=['no', 'yes'],
         help="Produce JSON output files as part of climatology generation") # same
      parser.add_argument('--netcdf', '-n', nargs=1, choices=['no', 'yes'],
         help="Produce NetCDF output files as part of climatology generation") # same
      parser.add_argument('--seasonally', action='store_true',
         help="Produce climatologies for all of the defined seasons. To get a list of seasons, run --list seasons")
      parser.add_argument('--monthly', action='store_true',
         help="Produce climatologies for all predefined months")
      parser.add_argument('--yearly', action='store_true',
         help="Produce annual climatogolies for all years in the dataset")
      parser.add_argument('--timestart', nargs=1,
         help="Specify the starting time for the dataset, such as 'months since Jan 2000'")
      parser.add_argument('--timebounds', nargs=1, choices=['daily', 'monthly', 'yearly'],
         help="Specify the time boudns for the dataset")
      parser.add_argument('--verbose', '-V', action='count',
         help="Increase the verbosity level. Each -v option increases the verbosity more.") # count
      parser.add_argument('--name', action='append', nargs=1,
         help="Specify option names for the datasets for plot titles, etc") #optional name for the set
      # This will be the standard list of region names NCAR has
      parser.add_argument('--region', '--regions', nargs='+', choices=self.all_regions,
         help="Specify a geographical region of interest")


      args = parser.parse_args()


      if(args.list != None):
         if args.list[0] == 'realms':
            print "Available realms: ", self.realm_types
            quit()

         if args.list[0] == 'seasons':
            print "Available seasons: ", self.all_seasons
            quit()

         if args.list[0] == 'packages':
            if args.realm == None:
               print "Please specify realm type before requesting packages list"
               quit()

            print "Listing available packages for type ", args.realm[0]
            plist = self.listPackages(args.realm)
            for p in plist:
               print p
#            for m in args.realm:
#               for n in self.all_packages[m]:
#                  print n
            quit()

         
         if args.list[0] == 'sets':
            if args.realm == None:
               print "Please specify realm type before requesting available diags sets"
               quit()
            if args.packages == None:
               print "Please specify package before requesting available diags sets"
               quit()
            for p in args.packages:
               print 'Avaialble sets for package ', p, ':'
               sets = self.listSets(p)
               for k in sets.keys():
                  print 'Set',k, ' - ', sets[k]
            quit()
               
         if args.list[0] == 'allsets':
            if args.realm == None:
               self.listAllSets()
            else:
               if args.packages == None:
                  self.listAllSets(realm=args.realm[0])
               else:
                  self.listAllSets(realm=args.realm[0], package=args.packages[0])
            quit()

         if args.list[0] == 'variables' or args.list[0] == 'vars':
            if args.path != None:
               for i in args.path:
                  self._opts['path'].append(i[0])
            else:
               print 'Must provide a dataset when requesting a variable listing'
               quit()
            self.listVariables(args.packages, args.sets)
            quit()

      print 'passed by list options, badness'
      quit()
      # TODO: If realm/package/set are not specified and --list is not passed, this would generally be an error


      if(args.path != None):
         for i in args.path:
            self._opts['path'].append(i[0])
      else:
         print 'Must specify a path at a minimum.'
         quit()

      if(args.obspath != None):
         for i in args.obspath:
            self._opts['obspath'].append(i[0])

      if(args.filter != None):
         self._opts['filter'] = args.filter[0]
#         for i in args.filter:
#            self._opts['filter'].append(i[0])

      self._opts['seasonally'] = args.seasonally
      self._opts['monthly'] = args.monthly

      if(args.compress != None):
         if(args.compress[0] == 'no'):
            self._opts['compress'] = False
         else:
            self._opts['compress'] = True

      if(args.json != None):
         if(args.json[0] == 'no'):
            self._opts['json'] = False
         else:
            self._opts['json'] = True

      if(args.netcdf != None):
         if(args.netcdf[0] == 'no'):
            self._opts['netcdf'] = False
         else:
            self._opts['netcdf'] = True

      if(args.plots != None):
         if(args.plots[0] == 'no'):
            self._opts['plots'] = False
         else:
            self._opts['plots'] = True

      if(args.climatologies != None):
         if(args.climatologies[0] == 'no'):
            self._opts['climatologies'] = False
         else:
            self._opts['climatologies'] = True

      self._opts['verbose'] = args.verbose

      if(args.name != None):
         for i in args.name:
            self._opts['dsnames'].append(i[0])

      # Timestart assumes a string like "months since 2000". I can't find documentation on
      # toRelativeTime() so I have no idea how to check for valid input
      # This is required for some of the land model sets I've seen
      if(args.timestart != None):
         self._opts['reltime'] = args.timestart
         
      # cdutil.setTimeBounds{bounds}(variable)
      if(args.timebounds != None):
         self._opts['bounds'] = args.timebounds

      # Check for a specified realm being valid
      if(args.realm != None):
         if(args.realm[0] in self.realm_types):
            self._opts['realm'] = args.realm[0]
         else:
            print 'realm type ',args.realm[0],' is not in the supported list'
            print 'Supported realm types: '
            for realm in self.realm_types:
               print realm
            quit()


      if(args.packages != None and self._opts['realm'] != None):
         plist = []
         # package was specified, and a realm has been picked
         for m in args.packages:
            for p in self.all_packages[self._opts['realm']]:
               if m == p:
                  plist.append(m)
         if plist == []:
            print 'Package name(s) ', args.packages, ' not valid'
            quit()
         else:
            self._opts['packages'] = plist


      # Given user-selected packages, check for user specified sets
      # Note: If multiple packages have the same set names, then they are all added to the list.
      # This might be bad since there is no differentiation of lwmg['id==set'] and lmwg2['id==set']
      if(args.sets != None and self._opts['packages'] != None):
         slist = []
         for p in self._opts['packages']:
            for user in args.sets:
               for s in self.all_sets[p]:
                  if user == s:
                     slist.append(user)
         self._opts['sets'] = slist

      # There is no way to check this yet since we have some derived variables in a lot of sets
      if args.vars != None:
         self._opts['vars'] = args.vars

      # If --yearly is set, then we will add 'ANN' to the list of climatologies
      if(args.yearly == True):
         self._opts['yearly'] = True
         self._opts['times'].append('ANN')

      # If --monthly is set, we add all months to the list of climatologies
      if(args.monthly == True):
         self._opts['monthly'] = True
         self._opts['times'].extend(self.all_months)

      # If --seasonally is set, we add all 4 seasons to the list of climatologies
      if(args.seasonally == True):
         self._opts['seasonally'] = True
         self._opts['times'].extend(self.all_seasons)

      # This allows specific individual months to be added to the list of climatologies
      if(args.months != None):
         if(args.monthly == True):
            print "Please specify just one of --monthly or --months"
            quit()
         else:
            mlist = []
            for m in self.all_months:
               for u in args.months:
                  if m == u:
                     mlist.append(u)
            self._opts['times'] = self._opts['times']+mlist

      # This allows specific individual years to be added to the list of climatologies.
      # Note: Checkign for valid input is impossible until we look at the dataset
      # This has to be special cased since typically someone will be saying
      # "Generate climatologies for seasons for years X, Y, and Z of my dataset"
      if(args.years != None):
         if(args.yearly == True):
            print "Please specify just one of --yearly or --years"
            quit()
         else:
            self._opts['years'] = args.years

      if(args.seasons != None):
         if(args.seasonally == True):
            print "Please specify just one of --seasonally or --seasons"
            quit()
         else:
            slist = []
            for s in self.all_seasons:
               for u in args.seasons:
                  if s == u:
                     slist.append(u)
            self._opts['times'] = self._opts['times']+slist



if __name__ == '__main__':
   o = Options()
   o.processCmdLine()
   print o._opts

