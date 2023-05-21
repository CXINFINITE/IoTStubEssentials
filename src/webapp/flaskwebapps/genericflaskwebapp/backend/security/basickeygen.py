import secrets

class BasicKeygen:
   def key_general_generate (length=None):
      if ((not length) or (length < 16)):
         length = 64
      
      key = secrets.token_urlsafe(length)
      
      return key
