import frontend.options

class TreeView():
   
   def __init__(self):
      self.tree = {}
      pass

   def makeTree(self, options, filetables, packages=None, user=None, ftnames=None):
      if user == None:
         username = 'User1'
      ### Assume realm has been predetermined, and only packages and beyond are of interest.
      ### ie, the script calling this function has already set up realm at least.

      self.tree['name'] = username
      self.tree['url'] = 'some top level url'
      self.tree['children'] = []

      if packages == None:
         packs = options._opts['packages']
      else:
         packs = packages

      for pack in packs:
         p = {}
         p['name'] = pack
         p['children'] = []
         for ds in range(len(filetables)):
            dataset = {}
            if ftnames != None:
               dataset['name'] = ftnames[ds]
            else:
               dataset['name'] = 'Dataset '+str(ds)
            dataset['children'] = []
            keys = options.all_sets[pack].keys()
            keys.sort(key=lambda x:int(filter(str.isdigit,x)))
            for s in keys:
               sets = {}
               sets['name'] = s
               sets['children'] = []
               for v in filetables[ds].list_variables():
                  var = {}
                  var['name'] = v
                  var['children'] = []
                  for t in options._opts['times']:
                     times = {}
                     times['name'] = t
                     times['url'] = 'url:'+t+v+str(ds)
                     var['children'].append(times)
                  sets['children'].append(var)
               dataset['children'].append(sets)
            p['children'].append(dataset)
         self.tree['children'].append(p)

         return self.tree
   def dump(self, filename=None):
      if filename == None:
         fname = 'test.json'
      else:
         fname = filename
      f = open(fname, 'w')
      import json
      json.dump(self.tree, f, separators=(',',':'), indent=2)
      f.close()
   



if __name__ == '__main__':
   o = Options()
   o.processCmdLine()
   tree=TreeView()
   # need to make a filetable
   print o._opts

