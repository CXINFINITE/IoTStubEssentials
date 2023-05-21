import genericflaskwebapp as app

class User (app.database.modelenginebridge.models.Model):
   modelname = 'Users'
   
   username = app.database.modelenginebridge.models.Fields.Str(
      main=True,
   )
   
   name = app.database.modelenginebridge.models.Fields.Str(
      notnone=False,
   )
   
   password = app.database.modelenginebridge.models.Fields.Str(
      notnone=True,
   )
   
   def _set_username (self, username=None):
      if (not username):
         username = ''
      
      return (str(username).strip())
   
   def _set_name (self, name=None):
      if (not name):
         return ''
      
      return (str(name).strip())
   
   def _set_password (self, password=None):
      if (not password):
         password = ''
      
      password = app.backend.security.passwordhasher.hash_password(
         password,
      )
      
      return password
   
   def check_password (self, password):
      result = app.backend.security.passwordhasher.hash_verify(
         password, self.password,
      )
      
      if (result):
         return True
      
      return False
   
   @classmethod
   def get_user (cls, username):
      user = cls.find(username=str(username).strip())
      
      if (user):
         return user
      
      return None
   
   @classmethod
   def get_authenticated_user (cls, username, password):
      user = cls.get_user(username=username)
      
      if (user
         and user.check_password(password=password)
      ):
         return user
      
      return None
