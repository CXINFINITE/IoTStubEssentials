from secrets import token_hex
from threading import Lock

class Identifier:
   _identity_lock = Lock()
   
   identity_active = dict() # id -> owner
   
   def _generate (identifier_length=16):
      identifier = None
      
      Identifier._identity_lock.acquire()
      
      try:
         while ((not identifier)
            or (identifier in Identifier.identity_active.keys())
         ):
            identifier = token_hex(identifier_length)
      finally:
         Identifier._identity_lock.release()
      
      return identifier
   
   def generate (owner, identifier_length=16):
      identifier = Identifier._generate(identifier_length=identifier_length)
      
      Identifier._identity_lock.acquire()
      
      try:
         Identifier.identity_active[identifier] = str(owner)
      finally:
         Identifier._identity_lock.release()
      
      return identifier
   
   def delete (identifier):
      Identifier._identity_lock.acquire()
      
      try:
         if (identifier in Identifier.identity_active.keys()):
            try:
               owner = Identifier.identity_active.pop(identifier)
            except:
               owner = True
            
            return owner
      finally:
         Identifier._identity_lock.release()
      
      return False
   
   def identify (identifier):
      result = None
      
      Identifier._identity_lock.acquire()
      
      try:
         result = Identifier.identifier_active.get(identifier, False)
      finally:
         Identifier._identity_lock.release()
      
      return result
