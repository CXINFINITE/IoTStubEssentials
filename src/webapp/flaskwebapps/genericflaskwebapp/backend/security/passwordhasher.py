import os
import hashlib

class PasswordHasher:
   def hash_password (password):
      salt = os.urandom(64)
      
      hashed = hashlib.sha3_512(password.encode())
      hashed.update(salt)
      hashed = hashed.hexdigest()
      
      result = (hashed, salt.hex())
      
      result = '$SHA3_512|$|{0}|$|{1}$'.format(
         *result,
      )
      
      return result
   
   def hash_verify (password, hashed):
      algorithm, hashed, salt = hashed.strip().split('|$|')
      
      if (algorithm[1:] != 'SHA3_512'):
         return None
      
      salt = salt[:-1]
      
      password = hashlib.sha3_512(password.encode())
      password.update(bytes.fromhex(salt))
      password = password.hexdigest()
      
      if (password == hashed):
         return True
      
      return False
