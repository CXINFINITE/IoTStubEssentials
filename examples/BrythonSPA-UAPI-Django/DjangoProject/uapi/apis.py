from .uapiManager import UAPIManager
from .apiUtilities import APIUtilities
from .apiDecorators import APIDecorators

# Use UAPI modules as:
# UAPIManager.function()
# APIUtilities.utility()
# @APIDecorators.decorator
# And so on ...

class APIs:
   loaded = None
   apis = dict()
   
   def start ():
      if (APIs.loaded):
         return None
      
      APIs.apis = {
         'api.getcodes': (APIs.api_getcodes, 0,),
         'api.test': (APIs.api_test, 10),
         
         # Either append all api functions (as shown above) here.
         # Or user UAPIManager.registerAPI to register during runtime or
         # on load.
         
         # Feel free to import function from anywhere.
      }
      
      for apicode, api_details in APIs.apis.items():
         UAPIManager.registerAPI(apicode, *api_details)
      
      APIs.loaded = True
   
   # Here are some example api_functions.
   # Do define your own ones here as required.
   
   def api_test (request=None, data=None, *args,):
      return UAPIManager.createResponse(
         status=True, reason=UAPIManager.Status.Reason.MY_REASON,
         responseData='This U-API system works!', yourData=data,
         sentargs=args,
      )
   
   def api_getcodes (request=None, data=None):
      return UAPIManager.createResponse(
         status=True, apicodes=list(UAPIManager.getAvailableAPIs()),
      )
