class Configuration:
   appUrl = None
   staticUrl = None
   brandImageUrl = 'Images/logo.png'
   
   loggedIn = None
   
   appName = 'WebApplication'
   applicationName = None
   subApplicationName = None
   pageStructureType = None
   
   connectionBlocking = True
   connectionTimeout = 3000 # int, msec
   ajaxMethod = 'POST'
   ajaxCaching = False
   
   failureMaxRetries = 3 # int, times
   failureRefreshInterval = 1000 # int, msec
