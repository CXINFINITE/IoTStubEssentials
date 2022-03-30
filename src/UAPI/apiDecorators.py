import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import UAPI

class APIDecorators:
   # Add your function decorators here.
   # Here's one example for you, for illustrative purpose only.
   '''
   def decorator1 (arg1=None, default_reason=None):
      if (not default_reason):
         default_reason = UAPI.UAPIManager.Status.Reason.MY_REASON
      
      def Inner (api_function):
         def wrapper (*args, **kwargs):
            if (not some_condition):
               return UAPI.UAPIManager.createResponse(
                  status=False,
                  reason=UAPI.UAPIManager.Status.Reason.INTERNAL_ERROR,
               )
            
            # check conditions here ...
            
            ok_condition = UAPI.APIUtilities.my_utility(*args, **kwargs)
            
            if (not ok_condition):
               return UAPI.UAPIManager.createResponse(
                  status=False,
                  reason=default_reason,
               )
            elif (ok_condition):
               return api_function(*args, **kwargs)
         
         return wrapper
      return Inner
   '''
