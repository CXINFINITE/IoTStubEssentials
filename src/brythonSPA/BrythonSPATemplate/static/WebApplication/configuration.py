class Configuration:
   appUrl = None
   staticUrl = None
   brandImageUrl = 'Images/logo.png'
   
   loggedIn = None
   
   appName = 'WebApplication'
   applicationName = None
   subApplicationName = None
   pageStructureType = None
   
   STATUS_SUCCESS = 'success'
   STATUS_CONNECTION_ERROR = 'connection error'
   
   apiErrorData = {'status': 'connection error',}
   
   connectionBlocking = True
   connectionTimeout = 3000 # int, msec
   ajaxMethod = 'POST'
   ajaxCaching = False
   
   failureMaxRetries = 3 # int, times
   failureRefreshInterval = 1000 # int, msec
   
   statusPollingInterval = 1500 # int, msec
