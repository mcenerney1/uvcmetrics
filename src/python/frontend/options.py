import argparse

class Options():
   all_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
   all_seasons = ['DJF', 'MAM', 'JJA', 'SON']
   all_models = ['atmosphere', 'land', 'test1']
   all_packages = {'atmosphere':['AMWG', 'atmotest1', 'atmotest2'], 'land': ['LMWG', 'landtest']}
   all_sets = {'LMWG':[{'id': 'Set1', 
                 'name': 'Line Plots of Annual Trends in Energy Balance, Soil water/ice temperature, runoff, snow water/ice, photosynthesis', 
                 'type': 'line', 
                 'climatology': ['annual'], 
                 'status':'active'},
                 {'id':'Set2',
                  'name': 'Horizontal contour plots of DJF, MAM, JJA, SON, and ANN means', 
                  'type':'contour',
                  'climatology': ['seasonal', 'annual'], 
                  'status':'active'},
                 {'id':'Set3',
                  'name': 'Line plots of monthly climatology: regional air temperature, precipitation, runoff, snow depth, radiative fluxes, and turbulent fluxes', 
                  'type':'line', 
                  'climatologies':['monthly'], 
                  'status':'active'},
                  {'id':'Set4',
                  'name':'Vertical Profiles at selected land raobs stations',
                  'type':None,
                  'climatologies':[],
                  'status':'inactive'},
                  {'id':'Set5',
                  'name':'Tables of annual means',
                  'type':'table',
                  'climatologies':['annual'],
                  'status':'active'},
                  {'id':'Set6',
                  'name':'Line plotso f annual trends in regional soil water/ice and temperature, runoff, snow, water/ice, photosynthesis',
                  'type':'regionalline',
                  'climatologies':['annual'],
                  'status':'active'},
                  {'id':'Set7',
                  'name':'Line plots, tables, and maps of RTM river flow and discharge to oceans',
                  'type':['line','table','maps'],
                  'climatologies':['annual'],
                  'status':'active'},
                  {'id':'Set8',
                  'name':'Line and contour plots of Ocean/Land.Atmosphere CO2 Exchange',
                  'type':['line','countour'],
                  'climatologies':None,
                  'status':'inactive'},
                  {'id':'Set9',
                  'name':'Contour plots and statistics for precipitation and temperature. Statistics include DJF, JJA, and ANN biases and RMSE, correlation and standard deviation of the annual cycle relative to observations',
                  'type':'contour',
                  'climatologies':['annual', 'seasonal'],
                  'status':'inactive'}],

                  'AMWG':[{'id':'Set1'}],
                  'landtest':[{'id':'Set1'}]}


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
      self._opts['times'] = []
      self._opts['model'] = None
      self._opts['packages'] = None
      self._opts['vars'] = None
      self._opts['sets'] = None
      self._opts['years'] = None
      self._opts['reltime'] = None
      self._opts['bounds'] = None
      self._opts['dsnames'] = []
      self._opts['filter'] = None


   def printsomething(self):
      print "Stuff"

   def processCmdLine(self):
      parser = argparse.ArgumentParser(
         description='UV-CDAT Climate Modeling Diagnostics', 
         usage='%(prog)s path1 [path2] [options]')

      parser.add_argument('--path', '-p', action='append', nargs=1, required=True, 
         help="Path to dataset(s). At least one path is required.")
      parser.add_argument('--model', '-m', nargs=1, choices=self.all_models, required=True , 
         help="The model type. Current valid options are 'land' and 'atmosphere'")
      parser.add_argument('--filter', '-f', nargs=1, 
         help="A filespec filter. This will be applied to the dataset path(s) to narrow down file choices.")
      parser.add_argument('--package', '-k', nargs='+', 
         help="The diagnostic packages to run against the dataset(s). Multiple packages can be specified.")
      parser.add_argument('--sets', '-s', nargs='+', 
         help="The sets within a diagnostic package to run. Multiple sets can be specified. If multiple packages were specified, the sets specified will be searched for in each package") 
      parser.add_argument('--vars', '-v', nargs='+', 
         help="Specify variables of interest to process.") 
      parser.add_argument('--list', '-l', nargs=1, choices=['sets', 'variables', 'packages', 'models'], 
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
      parser.add_argument('--json', '-j', action='store_true') # same
      parser.add_argument('--netcdf', '-n', action='store_true') # same
      parser.add_argument('--seasonally', action='store_true')
      parser.add_argument('--monthly', action='store_true')
      parser.add_argument('--yearly', action='store_true')
      parser.add_argument('--timestart', nargs=1)
      parser.add_argument('--timebounds', nargs=1, choices=['daily', 'monthly', 'yearly'])
      parser.add_argument('--verbose', '-V', action='count') # count
      parser.add_argument('--name', action='append', nargs=1) #optional name for the set

      args = parser.parse_args()

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
      self._opts['filter'] = args.filter

      
      if(args.name != None):
         for i in args.name:
            self._opts['dsnames'].append(i[0])

      # Timestart assumes a string like "months since 2000". I can't find documentation on
      # toRelativeTime() so I have no idea how to check for valid input
      if(args.timestart != None):
         self._opts['reltime'] = args.timestart
         
      # cdutil.setTimeBounds{bounds}(variable)
      if(args.timebounds != None):
         self._opts['bounds'] = args.timebounds

      # Check for a specified model being valid
      if(args.model != None and args.model[0] in self.all_models):
         self._opts['model'] = args.model[0]
      else:
         print 'model type ',args.model[0],' is not in the supported list'
         print 'Supported models types: '
         for model in self.all_models:
            print model
         quit()

      # Given a model, check for a specified package being valid
      # Note: This is more complicated if we allow multiple packages for a given model
      # (which is a reasonable thing to do)
      if(args.package != None and self._opts['model'] != None):
         plist = []
         # package was specified, and a model has been picked
         for m in args.package:
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
            for s in self.all_sets[p]:
               for user in args.sets:
                  if user == s['id']:
                     slist.append(user)

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

      if(args.list != None):
         if args.list[0] == 'models':
            print "Available models: ", self.all_models

         if args.list[0] == 'packages':
            if self._opts['model'] == None:
               print "Please specify model type before requesting packages"
               quit()

            print "Listing available packages for type ", self._opts['model']
            for n in self.all_packages[self._opts['model']]:
               print n

         if args.list[0] == 'sets':
            if self._opts['model'] == None:
               print "Please specify model type before requesting available diags sets"
               quit()
            if self._opts['packages'] == None:
               print "Please specify package before requesting available diags sets"
               quit()
            for p in self._opts['packages']:
               print "Available sets for package ", p, ":"
               for n in self.all_sets[p]:
                  print n['id']
               

         if args.list[0] == 'variables':
            if self._opts['model'] == None:
               print "Please specify model type before requesting available variables"
               quit()
            if self._opts['packages'] == None:
               print "Please specify package before requesting available variables"
               quit()
            if self._opts['sets'] == None:
               print "Please specify which sets to run before requesting available variables"
               quit()

            print "Not sure how to list variables yet; requires knowledge of derived variables from individual packages"


if __name__ == '__main__':
   o = Options()
   o.processCmdLine()
   print o._opts

