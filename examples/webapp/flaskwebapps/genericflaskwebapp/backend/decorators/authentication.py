from functools import wraps

from flask import (
   redirect,
)

import genericflaskwebapp as app

class Authentication:
   def login_required (
      redirectionroute,
      internalredirect=False,
      invert=False,
      **internalredirectiondata,
   ):
      def Inner (api_function):
         @wraps(api_function)
         def wrapper (*args, **kwargs):
            logged_in = (
               app.backend.functionality.Authentication.state_logged_in_check()
            )
            
            logged_in = (
               bool(logged_in[0])
               if (not invert)
               else
               bool(not logged_in[0])
            )
            
            if (not logged_in):
               if (internalredirect):
                  return app.backend.core.redirect_internal.redirect(
                     redirectionroute,
                     **internalredirectiondata,
                  )
               
               return redirect(redirectionroute)
            
            return api_function(*args, **kwargs)
         
         return wrapper
      return Inner
   
   def get_logged_in_user ():
      def Inner (api_function):
         @wraps(api_function)
         def wrapper (*args, **kwargs):
            return api_function(
               *args,
               user=(
                  app.backend.functionality.Authentication.get_logged_in_user()
               ),
               **kwargs,
            )
         
         return wrapper
      return Inner
