from functools import wraps

import genericflaskwebapp as app

class Redirect_Internal:
   def check (
      redirectionroute,
   ):
      def Inner (api_function):
         @wraps(api_function)
         def wrapper (*args, **kwargs):
            return api_function(
               *args,
               redirectiondata=(app.backend.core.redirect_internal.check(
                  redirectionroute,
               ) or dict()),
               **kwargs,
            )
         
         return wrapper
      return Inner
