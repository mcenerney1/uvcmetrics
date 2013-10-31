import argparse
import packages

#### NEED A REGIONS selection probably and maybe list of regions?

class Options():
   all_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
   all_seasons = ['DJF', 'MAM', 'JJA', 'SON']

   def __init__(self):
      self._opts = {}
      self._opts['nc'] = False
      self._opts['seasonally'] = False
      self._opts['monthly'] = False
      self._opts['yearly'] = False
      self._opts['json'] = False
      self._opts['netcdf'] = False
      self._opts['climatologies'] = True
      self._opts['plots'] = True
      self._opts['precomputed'] = False
      self._opts['model'] = None
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

      # Generate a unique list of available model types
      self.model_types = packages.all_models
      self.all_packages = packages.all_packages

      self.all_sets = {}
      for m in self.model_types:
         for p in self.all_packages[m]:
            self.all_sets[p] = {}
            for s in packages.__dict__[p].package_ids:
               self.all_sets[p][s] = packages.__dict__[p].package_sets[s]

#      print self.all_sets

   def listSeasons(self):
      return self.all_seasons;

   def listPlots(self, sets):
      return

   def listSets(self, package, key=None):
      if key != None:
         kys = self.all_sets[package].keys()
         # assume "setXX" where XX is a number and we want "10" after "9" not "1"
         kys.sort(key=lambda x:int(filter(str.isdigit, x)))
         klist = []
         for k in kys:
            klist.append(self.all_sets[package][k][key])
         return klist
      else:
         l = list(self.all_sets[package].keys())
         l.sort(key=lambda x:int(filter(str.isdigit, x)))
         return l
#         return list(self.all_sets[package].keys()).sort(key=lambda x:int(x[3:]))
#         return self.all_sets[package].keys()
      #return self.all_sets[model][package]

   def listModels(self):
      return self.all_models

   def listPackages(self, model):
      if type(model) == list:
         plist = []
         for m in model:
            plist.append(self.all_packages[m])
         return plist
      else:
         return self.all_packages[model]


   def processCmdLine(self):
      parser = argparse.ArgumentParser(
         description='UV-CDAT Climate Modeling Diagnostics', 
         usage='%(prog)s path1 [path2] [options]')

      parser.add_argument('--path', '-p', action='append', nargs=1, required=True, 
         help="Path to dataset(s). At least one path is required.")
      parser.add_argument('--model', '-m', nargs=1, choices=self.model_types,
         help="The model type. Current valid options are 'land' and 'atmosphere'")
      parser.add_argument('--filter', '-f', nargs=1, 
         help="A filespec filter. This will be applied to the dataset path(s) to narrow down file choices.")
      parser.add_argument('--packages', '--package', '-k', nargs='+', 
         help="The diagnostic packages to run against the dataset(s). Multiple packages can be specified.")
      parser.add_argument('--sets', '--set', '-s', nargs='+', 
         help="The sets within a diagnostic package to run. Multiple sets can be specified. If multiple packages were specified, the sets specified will be searched for in each package") 
      parser.add_argument('--vars', '--var', '-v', nargs='+', 
         help="Specify variables of interest to process. The default is all variables which can also be specified with the keyword ALL") 
      parser.add_argument('--list', '-l', nargs=1, choices=['sets', 'variables', 'packages', 'models', 'seasons', 'plottypes'], 
         help="Determine which models, packages, sets, and variables are available")
      parser.add_argument('--nc', action='store_true', 
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
      parser.add_argument('--json', '-j', action='store_true',
         help="Produce JSON output files as part of climatology generation") # same
      parser.add_argument('--netcdf', '-n', action='store_true',
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
      parser.add_argument('--region', '--regions', nargs='+', choices=["North America", "South America"],
         help="Specify a geographical region of interest")


      args = parser.parse_args()


      if(args.list != None):
         if args.list[0] == 'models':
            print "Available models: ", self.model_types

         if args.list[0] == 'seasons':
            print "Available seasons: ", self.all_seasons

         if args.list[0] == 'packages':
            if args.model == None:
               print "Please specify model type before requesting packages list"
               quit()

            print "Listing available packages for type ", args.model[0]
            plist = self.listPackages(args.model)
            for p in plist:
               print p
#            for m in args.model:
#               for n in self.all_packages[m]:
#                  print n

         if args.list[0] == 'sets':
            if args.model == None:
               print "Please specify model type before requesting available diags sets"
               quit()
            if args.packages == None:
               print "Please specify package before requesting available diags sets"
               quit()
            for p in args.packages:
               print 'Avaialble sets for package ', p, ':'
               print self.listSets(p)
               

         if args.list[0] == 'variables':
            print "Listing variables not yet supported"
            quit()
            #print "Not sure how to list variables yet; requires knowledge of derived variables from individual packages"

         # Stop processing arguments if list was requested
         quit()

      # TODO: If model/package/set are not specified and --list is not passed, this would generally be an error

      if(args.path != None):
         for i in args.path:
            self._opts['path'].append(i[0])
      else:
         print 'Must specify a path at a minimum.'
         quit()

      if(args.filter != None):
         for i in args.filter:
            self._opts['filter'].append(i[0])

      self._opts['nc'] = args.nc
      self._opts['seasonally'] = args.seasonally
      self._opts['monthly'] = args.monthly
      self._opts['json'] = args.json
      self._opts['netcdf'] = args.netcdf
      if(self._opts['plots'] != None):
         if(self._opts['plots'] == 'no'):
            args.plots = False
         else:
            args.plots = True

      self._opts['plots'] = args.plots

      if(self._opts['climatologies'] != None):
         if(self._opts['climatologies'] == 'no'):
            args.climatologies = False
         else:
            args.climatologies = True

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

      # Check for a specified model being valid
      if(args.model == None):
         print "Please provide a model. Supported model types are: "
         for model in self.model_types:
            print model
         quit()
      else:
         if(args.model[0] in self.model_types):
            self._opts['model'] = args.model[0]
         else:
            print 'model type ',args.model[0],' is not in the supported list'
            print 'Supported models types: '
            for model in self.model_types:
               print model
            quit()

      # Given a model, check for a specified package being valid
      # Note: This is more complicated if we allow multiple packages for a given model
      # (which is a reasonable thing to do)
      if(args.packages == None):
         print "Please specify a package name"
         quit()

      if(args.packages != None and self._opts['model'] != None):
         plist = []
         # package was specified, and a model has been picked
         for m in args.packages:
            for p in self.all_packages[self._opts['model']]:
               if m == p:
                  plist.append(m)
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
      self._opts['vars'] == args.vars

      # If --yearly is set, then we will add 'ANN' to the list of climatologies
      if(args.yearly == True):
         self._opts['yearly'] = True
         self._opts['times'] = self._opts['times']+'ANN'

      # If --monthly is set, we add all months to the list of climatologies
      if(args.monthly == True):
         self._opts['monthly'] = True
         self._opts['times'] = self._opts['times']+self.all_months

      # If --seasonally is set, we add all 4 seasons to the list of climatologies
      if(args.seasonally == True):
         self._opts['seasonally'] = True
         self._opts['times'] = self._opts['times']+self.all_seasons

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

