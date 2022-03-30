import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent.parent
))

import BrythonModulesUpdater as App

class Executor:
   def execute_from_cli ():
      App.ArgParser.start()
      
      if (not Executor.updateConfig(App.ArgParser.parse_args())):
         return None
      
      status = App.core.ModulesUpdater.run()
      
      if (App.Configuration.verbose < 1): pass
      elif (App.Configuration.verbose < 2):
         print('Status:', App.core.ModulesUpdater.operationStatus)
      else:
         for status in App.core.ModulesUpdater.netStatus:
            if (type(status[1]).__name__ in ('tuple', 'list',)):
               print('{0}: -----'.format(status[0]))
               for mstatus in status[1]:
                  if (type(mstatus).__name__ in ('tuple', 'list',)):
                     print('{0}{1}: {2}'.format(
                        (' ' * (len(status[0]) + 2)),
                        mstatus[0], mstatus[1],
                     ))
                  else:
                     print('{0}{1}'.format(
                        (' ' * (len(status[0]) + 2)),
                        mstatus,
                     ))
               print('{0}{1}'.format(('-' * (len(status[0]) + 2)), '-----'),)
            else:
               print('{0}: {1}'.format(status[0], status[1]))
      
      if (status): print('\nModules updated successfully!')
      else: print('\nModule updation failure!')
      
      return status
   
   def updateConfig (config):
      if (not config.applicationName):
         return False
      
      App.Configuration.applicationName = config.applicationName
      App.Configuration.subApplicationName = config.subApplicationName or None
      
      App.Configuration.basePath = config.basePath or (
         App.Configuration.basePath
      )
      App.Configuration.baseApplicationName = config.baseApplicationName or (
         App.Configuration.baseApplicationName
      )
      App.Configuration.jsDirPath = config.jsDirPath or (
         (App.Configuration.basePath / 'JS').resolve()
      )
      
      if (config.requiredAppFiles):
         App.Configuration.requiredAppFiles = config.requiredAppFiles or (
            App.Configuration.requiredAppFiles
         )
      
      if (config.requiredAppDirs):
         App.Configuration.requiredAppDirs = config.requiredAppDirs or (
            App.Configuration.requiredAppDirs
         )
      
      App.Configuration.webPagesDirName = config.webPagesDirName or (
         App.Configuration.webPagesDirName
      )
      
      if (config.requiredWebPagesFiles):
         App.Configuration.requiredWebPagesFiles = (
            config.requiredWebPagesFiles
         ) or App.Configuration.requiredWebPagesFiles
      
      if (config.requiredWebPagesDirs):
         App.Configuration.requiredWebPagesDirs = (
            config.requiredWebPagesDirs
         ) or App.Configuration.requiredWebPagesDirs
      
      App.Configuration.brythonCliModulesCommand = (
         config.brythonCliModulesCommand
      ) or App.Configuration.brythonCliModulesCommand
      
      App.Configuration.verbose = config.verbose or App.Configuration.verbose
      App.Configuration.intermediateFiles = config.intermediateFiles
      
      return True
