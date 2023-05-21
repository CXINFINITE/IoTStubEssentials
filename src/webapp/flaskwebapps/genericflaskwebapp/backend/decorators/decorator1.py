from functools import wraps

import genericflaskwebapp as app

def decorator1 (*decoratorargs, **decoratorkwargs):
   # Your code here !
   
   def Inner (api_function):
      @wraps(api_function)
      def wrapper (*args, **kwargs):
         # Your code here (AND) OR
         return api_function(*args, **kwargs)
      
      return wrapper
   return Inner
