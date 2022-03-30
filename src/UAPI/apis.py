import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import UAPI

# Use other UAPI modules as:
# UAPI.UAPIManager.function()
# UAPI.APIUtilities.utility()
# @UAPI.APIDecorators.decorator
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
         # Or user UAPI.UAPIManager.registerAPI to register during runtime or
         # on load.
         
         # Feel free to import function from anywhere.
      }
      
      for apicode, api_details in APIs.apis.items():
         UAPI.UAPIManager.registerAPI(apicode, *api_details)
      
      APIs.loaded = True
   
   # Here are some example api_functions.
   # Do define your own ones here as required.
   
   def api_test (request=None, data=None, *args,):
      return UAPI.UAPIManager.createResponse(
         status=True, reason=UAPI.UAPIManager.Status.Reason.MY_REASON,
         responseData='This U-API system works!', yourData=data,
         sentargs=args,
      )
   
   def api_getcodes (request=None, data=None):
      return UAPI.UAPIManager.createResponse(
         status=True, apicodes=list(UAPI.UAPIManager.getAvailableAPIs()),
      )
