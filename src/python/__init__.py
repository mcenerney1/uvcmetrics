#  put here the import calls to expose whatever we want to the user
try:
   import fileio
   import computation
   import frontend
except:
   import metrics.fileio
   import metrics.computation
   import metrics.frontend

import git
