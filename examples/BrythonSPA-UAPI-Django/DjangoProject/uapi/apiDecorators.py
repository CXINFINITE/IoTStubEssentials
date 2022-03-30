from .uapiManager import UAPIManager

from .apiUtilities import APIUtilities

class APIDecorators:
   # Add your function decorators here.
   # Here's one example for you, for illustrative purpose only.
   '''
   def decorator1 (arg1=None, default_reason=None):
      if (not default_reason):
         default_reason = UAPIManager.Status.Reason.MY_REASON
      
      def Inner (api_function):
         def wrapper (*args, **kwargs):
            if (not some_condition):
               return UAPIManager.createResponse(
                  status=False,
                  reason=UAPIManager.Status.Reason.INTERNAL_ERROR,
               )
            
            # check conditions here ...
            
            ok_condition = APIUtilities.my_utility(*args, **kwargs)
            
            if (not ok_condition):
               return UAPIManager.createResponse(
                  status=False,
                  reason=default_reason,
               )
            elif (ok_condition):
               return api_function(*args, **kwargs)
         
         return wrapper
      return Inner
   '''
