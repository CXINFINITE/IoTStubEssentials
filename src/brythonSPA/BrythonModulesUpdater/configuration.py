from pathlib import Path

class Configuration:
   appName = 'BrythonModulesGenerator'
   version = '0.0.0'
   
   verbose = 0
   intermediateFiles = None
   tempDirNameRetryLimit = 100
   
   basePath = (
      Path(__file__).resolve().parent.parent / (
         'BrythonSPATemplate'
      ) / 'static'
   ).resolve()
   baseApplicationName = 'WebApplication'
   jsDirPath = None # defaults to basePath / JS
   
   applicationName = None
   subApplicationName = None
   
   moduleFilesDir = (Path(__file__).resolve().parent / (
      'modulefiles'
   )).resolve()
   requiredModuleFiles = (
      'brython.js',
      'brython_stdlib.js',
   )
   
   brythonCliModulesCommand = 'brython-cli --modules'
   
   tempDirFormat = "TEMPDIR" + appName + "_temp{0}TEMPDIR"
   tempDir = None
   
   requiredAppFiles = (
      '__init__.py',
      'configuration.py',
   )
   requiredAppDirs = (
      'core',
      'webInterface',
   )
   webPagesDirName = 'webPages'
   requiredWebPagesFiles = (
      'pageStructure.py',
   )
   requiredWebPagesDirs = []
