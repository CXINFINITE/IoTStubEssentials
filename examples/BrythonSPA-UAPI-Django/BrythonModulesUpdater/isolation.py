import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import BrythonModulesUpdater as App

class Isolation:
   tempDir = None
   
   operationStatus = []
   
   def generateTempDir ():
      status = []
      
      tempdir = str(App.Configuration.tempDirFormat).format(
         '{0}_{1}'.format(
            App.Configuration.baseApplicationName,
            (App.Configuration.applicationName
               if (not App.Configuration.subApplicationName)
               else (
                  '{0}_{1}'.format(
                     App.Configuration.applicationName,
                     App.Configuration.subApplicationName,
                  )
               )
            ),
         )
      )
      
      if (os.path.exists(App.Configuration.basePath / tempdir)):
         mstatus = []
         climit = App.Configuration.tempDirNameRetryLimit
         tempdir += '_r'
         ctempdir = tempdir
         tempdirnum = 0
         
         while True:
            climit -= 1
            tempdirnum += 1
            ctempdir = '{0}{1}'.format(tempdir, tempdirnum)
            
            if (climit < 1):
               break
            
            if (os.path.exists(App.Configuration.basePath / ctempdir)):
               mstatus.append(False)
               continue
            else:
               mstatus.append(True)
               break
         
         tempdir = ctempdir
         
         if (os.path.exists(App.Configuration.basePath / tempdir)):
            Isolation.operationStatus.append(
               ('generateTempDir', (mstatus,),)
            )
            return None
         else:
            status.append(mstatus)
      
      Isolation.tempDir = App.Configuration.basePath / tempdir
      App.Configuration.tempDir = Isolation.tempDir
      
      status.append(App.OSCommands.command('mkdir',
         os.path.abspath(Isolation.tempDir),
         run=True, quoteStr=True, addSep=True,
      ))
      
      Isolation.operationStatus.append(('generateTempDir', status,))
      
      return True
   
   def isolate ():
      status = []
      
      status.append(App.OSCommands.command('cp',
            os.path.abspath(
               App.Configuration.basePath / (
                  '{0}.py'.format(App.Configuration.baseApplicationName)
               )
            ),
            os.path.abspath(
               Isolation.tempDir / (
                  '{0}.py'.format(App.Configuration.baseApplicationName)
               )
            ),
            run=True, quoteStr=True,
         )
      )
      status.append(App.OSCommands.command('mkdir',
            os.path.abspath(
               Isolation.tempDir / App.Configuration.baseApplicationName
            ),
            run=True, quoteStr=True, addSep=True,
         )
      )
      
      mstatus = []
      for requiredAppFile in App.Configuration.requiredAppFiles:
         mstatus.append(App.OSCommands.command('cp',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / requiredAppFile
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / requiredAppFile
               ),
               run=True, quoteStr=True,
            )
         )
      
      status.append(mstatus.copy())
      mstatus = []
      for requiredAppDir in App.Configuration.requiredAppDirs:
         mstatus.append(App.OSCommands.command('cp -r',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / requiredAppDir
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / requiredAppDir
               ),
               run=True, quoteStr=True, addSep=True,
            )
         )
      
      status.append(mstatus.copy())
      
      status.append(App.OSCommands.command('mkdir',
            os.path.abspath(
               Isolation.tempDir / App.Configuration.baseApplicationName / (
                  App.Configuration.webPagesDirName
               )
            ),
            run=True, quoteStr=True, addSep=True,
         )
      )
      
      mstatus = []
      for requiredWebPagesFile in App.Configuration.requiredWebPagesFiles:
         mstatus.append(App.OSCommands.command('cp',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     requiredWebPagesFile
                  )
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     requiredWebPagesFile
                  )
               ),
               run=True, quoteStr=True,
            )
         )
      
      status.append(mstatus.copy())
      mstatus = []
      for requiredWebPagesDir in App.Configuration.requiredWebPagesDirs:
         mstatus.append(App.OSCommands.command('cp -r',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     requiredWebPagesDir
                  )
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     requiredWebPagesDir
                  )
               ),
               run=True, quoteStr=True, addSep=True,
            )
         )
      
      status.append(mstatus.copy())
      
      status.append(App.OSCommands.command('cp',
            os.path.abspath(
               App.Configuration.basePath / (
                  App.Configuration.baseApplicationName
               ) / App.Configuration.webPagesDirName / (
                  '{0}.__init__.py'.format(
                     App.Configuration.applicationName,
                  )
               )
            ),
            os.path.abspath(
               Isolation.tempDir / (
                  App.Configuration.baseApplicationName
               ) / App.Configuration.webPagesDirName / '__init__.py'
            ),
            run=True, quoteStr=True,
         )
      )
      
      if (not App.Configuration.subApplicationName):
         status.append(App.OSCommands.command('cp -r',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  )
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  )
               ),
               run=True, quoteStr=True, addSep=True,
            )
         )
      else:
         status.append(App.OSCommands.command('mkdir',
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  )
               ),
               run=True, quoteStr=True, addSep=True,
            )
         )
         
         status.append(App.OSCommands.command('cp',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  ) / (
                     '{0}.__init__.py'.format(
                        App.Configuration.subApplicationName,
                     )
                  )
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  ) / '__init__.py'
               ),
               run=True, quoteStr=True,
            )
         )
         
         status.append(App.OSCommands.command('cp -r',
               os.path.abspath(
                  App.Configuration.basePath / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  ) / App.Configuration.subApplicationName
               ),
               os.path.abspath(
                  Isolation.tempDir / (
                     App.Configuration.baseApplicationName
                  ) / App.Configuration.webPagesDirName / (
                     App.Configuration.applicationName
                  ) / App.Configuration.subApplicationName
               ),
               run=True, quoteStr=True, addSep=True,
            )
         )
      
      Isolation.operationStatus.append(('isolate', status,))
      
      return True
   
   def removeIsolation ():
      result = App.OSCommands.command('rm -r',
         os.path.abspath(
            Isolation.tempDir
         ),
         run=True, quoteStr=True,
      )
      
      Isolation.operationStatus.append(('removeIsolation', (result,),))
      
      return True
