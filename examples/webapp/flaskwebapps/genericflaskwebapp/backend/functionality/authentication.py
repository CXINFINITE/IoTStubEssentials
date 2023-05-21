from flask import (
   session,
)

import genericflaskwebapp as app

class Authentication:
   class ERROR:
      NONE = None
      ALREADY_LOGGED_IN = 'Already Logged In'
      ALREADY_LOGGED_OUT = 'Already Logged Out'
      MISSING_CREDENTIALS = 'Missing Credentials'
      SESSION_INVALID = 'Session Invalid'
      INVALID_CREDENTIALS = 'Invalid Credentials'
   
   def state_logged_in_check (username=None):
      userdata = session.get('user')
      
      if (not userdata):
         return (None, None)
      
      if (not (userdata.get('logged_in') and userdata.get('username'))):
         return (None, None)
      
      if (username and (username != userdata.get('username'))):
         return (None, None)
      
      return (True, userdata.get('username'))
   
   def state_clear_check (username):
      userdata = session.get('user')
      
      if (not userdata):
         return (True, Authentication.ERROR.NONE)
      
      if ((username == userdata.get('username'))
         and userdata.get('logged_in')
      ):
         return (True, Authentication.ERROR.ALREADY_LOGGED_IN)
      elif ((username == userdata.get('username'))
         and (not userdata.get('logged_in'))
      ):
         return (True, Authentication.ERROR.NONE)
      elif ((username != userdata.get('username'))
         and userdata.get('logged_in')
      ):
         return (None, Authentication.ERROR.SESSION_INVALID)
      
      return (True, Authentication.ERROR.NONE)
   
   def login (username, password):
      username = str(username).strip()
      password = str(password).strip()
      
      if (not (username and password)):
         return (None, Authentication.ERROR.MISSING_CREDENTIALS)
      
      currentstate = Authentication.state_clear_check(username)
      
      if (not currentstate[0]):
         return currentstate
      
      user = app.database.models.User.get_authenticated_user(
         username=username,
         password=password,
      )
      
      if (not user):
         return (None, Authentication.ERROR.INVALID_CREDENTIALS)
      
      userdata = {
         'logged_in': True,
         'username': username,
      }
      
      session['user'] = userdata
      
      return (True, Authentication.ERROR.NONE, user)
   
   def logout ():
      session.clear()
      
      return (True, Authentication.ERROR.NONE)
   
   def get_logged_in_user (username=None):
      if (username):
         username = str(username).strip()
      
      loggedinstate = Authentication.state_logged_in_check(username=username)
      
      if (not loggedinstate[0]):
         return None
      
      user = app.database.models.User.get_user(
         username=loggedinstate[-1],
      )
      
      if (not user):
         return None
      
      return user
