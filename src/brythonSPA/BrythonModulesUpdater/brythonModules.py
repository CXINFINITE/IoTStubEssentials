import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import BrythonModulesUpdater as App

class BrythonModules:
   operationStatus = []
   
   def loadModules ():
      status = []
      
      try:
         with open(
               str(os.path.abspath(App.Configuration.tempDir / 'index.html')),
               'w'
            ) as fh:
            fh.write(("""
                     <HTML>
                        <HEAD>
                           <TITLE>Index</TITLE>
                           
                           <script
                              type="text/python"
                              src="{0}.py"
                              id="__main__"
                           ></script>
                        </HEAD>
                        <BODY onload="brython(1)">
                           Index's body.
                        </BODY>
                     </HTML>
                  """.format(App.Configuration.baseApplicationName)
               ).strip()
            )
         status.append(True)
      except: status.append(None)
      
      mstatus = []
      
      for requiredModuleFile in App.Configuration.requiredModuleFiles:
         mstatus.append(App.OSCommands.command('cp',
               os.path.abspath(
                  App.Configuration.moduleFilesDir / requiredModuleFile
               ),
               os.path.abspath(
                  App.Configuration.tempDir / requiredModuleFile
               ),
               run=True, quoteStr=True,
            )
         )
      
      status.append(mstatus.copy())
      
      BrythonModules.operationStatus.append(('loadModules', status,))
      
      return True
   
   def generateModuleFile ():
      cd_command = App.OSCommands.command('cd',
         os.path.abspath(
            App.Configuration.tempDir
         ),
         run=False, quoteStr=True, addSep=True,
      )
      
      if (not cd_command): return None
      
      try:
         result = os.system('{0} && {1}'.format(
            cd_command,
            App.Configuration.brythonCliModulesCommand,
         ))
      except: result = None
      
      BrythonModules.operationStatus.append(('generateModuleFile', (result,),))
      
      return True
   
   def replaceModuleFile ():
      status = []
      
      status.append(App.OSCommands.command('rm',
            os.path.abspath(
               App.Configuration.jsDirPath / (
                  '{0}.{1}.brython_modules.js'.format(
                     App.Configuration.baseApplicationName,
                     (App.Configuration.applicationName
                        if (not App.Configuration.subApplicationName)
                        else (
                           '{0}.{1}'.format(
                              App.Configuration.applicationName,
                              App.Configuration.subApplicationName,
                           )
                        )
                     ),
                  )
               )
            ),
            run=True, quoteStr=True,
         )
      )
      
      if (App.Configuration.intermediateFiles):
         status.append(App.OSCommands.command('cp',
               os.path.abspath(
                  App.Configuration.tempDir / 'brython_modules.js'
               ),
               os.path.abspath(
                  App.Configuration.jsDirPath / (
                     '{0}.{1}.brython_modules.js'.format(
                        App.Configuration.baseApplicationName,
                        (App.Configuration.applicationName
                           if (not App.Configuration.subApplicationName)
                           else (
                              '{0}.{1}'.format(
                                 App.Configuration.applicationName,
                                 App.Configuration.subApplicationName,
                              )
                           )
                        ),
                     )
                  )
               ),
               run=True, quoteStr=True,
            )
         )
      else:
         status.append(App.OSCommands.command('mv',
               os.path.abspath(
                  App.Configuration.tempDir / 'brython_modules.js'
               ),
               os.path.abspath(
                  App.Configuration.jsDirPath / (
                     '{0}.{1}.brython_modules.js'.format(
                        App.Configuration.baseApplicationName,
                        (App.Configuration.applicationName
                           if (not App.Configuration.subApplicationName)
                           else (
                              '{0}.{1}'.format(
                                 App.Configuration.applicationName,
                                 App.Configuration.subApplicationName,
                              )
                           )
                        ),
                     )
                  )
               ),
               run=True, quoteStr=True,
            )
         )
      
      BrythonModules.operationStatus.append(('replaceModuleFile', status,))
      
      return True
