import datetime

from flask import (
   redirect,
   session,
)

class Redirect_Internal:
   def redirect (route, expire=None, **kwargs):
      redirectiondata = {
         'route': route,
         'data': kwargs,
         'expire': (None
            if (not expire)
            else
            expire
         ),
      }
      session['redirect_internal'] = redirectiondata
      
      return redirect(route)
   
   def check (route):
      if ('redirect_internal' not in session):
         return None
      
      redirectiondata = session.pop('redirect_internal')
      
      if (redirectiondata.get('route') != route):
         return None
      
      if (redirectiondata.get('expire')):
         if (
            datetime.datetime.now() > redirectiondata.get('expire')
         ):
            return None
      
      return (redirectiondata.get('data'))
