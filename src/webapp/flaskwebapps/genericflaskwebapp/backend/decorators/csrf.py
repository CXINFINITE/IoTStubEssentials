from functools import wraps

import genericflaskwebapp as app

class CSRF:
   def csrf_protect (
      embedd=True,
      check=True, form=None,
      ontrap=None, ontrapcallable=False, ontrapembedd=False,
   ):
      if (not (embedd or check)):
         raise Exception(
            'backend.decorators.csrf:csrf_protect:: csrf protection used but '
            + 'not enabled !'
         )
      
      def Inner (api_function):
         @wraps(api_function)
         def wrapper (*args, **kwargs):
            if (check
               and (not app.backend.security.csrf.check_csrf_token(form=form))
            ):
               if (ontrap):
                  if (ontrapembedd):
                     return app.backend.security.csrf.embedd_token((
                        ontrap()
                        if (callable(ontrap) and ontrapcallable)
                        else
                        ontrap
                     ))
                  
                  return (
                     ontrap()
                     if (callable(ontrap) and ontrapcallable)
                     else
                     ontrap
                  )
               
               return 'Request blocked !'
            
            if (embedd):
               return app.backend.security.csrf.embedd_token(
                  api_function(*args, **kwargs),
               )
            
            return api_function(*args, **kwargs)
         
         return wrapper
      return Inner
