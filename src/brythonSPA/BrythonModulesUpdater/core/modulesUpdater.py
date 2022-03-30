import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent.parent
))

import BrythonModulesUpdater as App

class ModulesUpdater:
   operationStatus = []
   netStatus = []
   
   def run ():
      def removeIsolation ():
         ModulesUpdater.updateStatus()
         
         if (App.Configuration.intermediateFiles):
            ModulesUpdater.operationStatus.append(True)
         else:
            ModulesUpdater.operationStatus.append(
               App.Isolation.removeIsolation()
            )
         
         return None
      
      status = App.Isolation.generateTempDir()
      ModulesUpdater.operationStatus.append(status)
      
      if (not status): return None
      
      status = App.Isolation.isolate()
      ModulesUpdater.operationStatus.append(status)
      
      if (not status): return removeIsolation()
      
      status = App.BrythonModules.loadModules()
      ModulesUpdater.operationStatus.append(status)
      
      if (not status): return removeIsolation()
      
      status = App.BrythonModules.generateModuleFile()
      ModulesUpdater.operationStatus.append(status)
      
      if (not status): return removeIsolation()
      
      ModulesUpdater.operationStatus.append(
         App.BrythonModules.replaceModuleFile()
      )
      
      removeIsolation()
      
      return True
   
   def updateStatus ():
      ModulesUpdater.netStatus = ((
         ('ModulesUpdater.run', ModulesUpdater.operationStatus),
         ('Isolation', App.Isolation.operationStatus),
         ('BrythonModules', App.BrythonModules.operationStatus),
      ))
