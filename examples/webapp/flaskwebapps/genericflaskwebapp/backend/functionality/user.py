import genericflaskwebapp as app

class User:
   class ERROR:
      NONE = None
      ACCOUNT_CREATION_FAILURE = 'Account creation failure'
      INCOMPLETE_DETAILS = 'Incomplete details'
      USERNAME_ALREADY_TAKEN = 'Username already taken'
      USERNAME_TOO_SHORT = 'Username too short'
      USERNAME_TOO_LONG = 'Username too long'
      NAME_TOO_SHORT = 'Name too short'
      USER_TOO_LONG = 'Name too long'
      PASSWORD_TOO_SHORT = 'Password too short'
      PASSWORD_TOO_LONG = 'Password too long'
   
   def create (username, name, password):
      if (not (username and name and password)):
         return (None, User.ERROR.INCOMPLETE_DETAILS)
      
      username = str(username).strip()
      name = str(name).strip()
      password = str(password).strip()
      
      if (not (username and name and password)):
         return (None, User.ERROR.INCOMPLETE_DETAILS)
      
      if (len(username) < 4):
         return (None, User.ERROR.USERNAME_TOO_SHORT)
      elif (len(username) > 16):
         return (None, User.ERROR.USERNAME_TOO_LONG)
      
      if (len(name) < 3):
         return (None, User.ERROR.NAME_TOO_SHORT)
      elif (len(name) > 64):
         return (None, User.ERROR.NAME_TOO_LONG)
      
      if (len(password) < 8):
         return (None, User.ERROR.PASSWORD_TOO_SHORT)
      elif (len(password) > 32):
         return (None, User.ERROR.PASSWORD_TOO_LONG)
      
      usernamenotunique = app.database.models.User.search_aggregate(
         select='username',
         aggregate=app.database.models.User.AGGREGATE.COUNT,
         username=username,
      )
      
      if (usernamenotunique.get('username')):
         return (None, User.ERROR.USERNAME_ALREADY_TAKEN)
      
      try:
         user = app.database.models.User(
            dbengine=app.database.engine,
            username=username,
            name=name,
            password=password,
         )
         user.save()
      except:
         user = None
      
      if (not user):
         return (None, User.ERROR.ACCOUNT_CREATION_FAILURE)
      
      return (True, user)
