import sqlite3

class SQLite3Engine:
   class FETCH:
      RAW = 1
      ONE = 2
      ALL = 3
   
   class ERROR:
      NONE = 0
      
      EXECUTION = 1
      COMMIT = 2
      FETCH = 4
   
   def __init__ (self, databasepath):
      if (not databasepath):
         raise ValueError(
            'database.engines.sqlite3engine:SQLite3Engine:: '
            + 'no databasepath supplied (\'{0}\')'.format(
               databasepath,
            )
         )
      
      self.connection = sqlite3.connect(
         databasepath,
         check_same_thread=False,
      )
      self.cursor = self.connection.cursor()
      self.connected = True
   
   def close (self, commit=False):
      if (self.connected):
         if (commit):
            try:
               self.connection.commit()
            except:
               pass
         
         try:
            self.connection.close()
         except:
            pass
         
         self.connected = False
         
         return True
      
      return False
   
   def wrapped_execution (self, function, *args, **kwargs):
      try:
         return function(*args, **kwargs)
      except:
         raise
      finally:
         self.close()
   
   def execute_raw (
      self,
      query, *args,
      fetch=None, commit=False, errorstatus=True,
      **kwargs,
   ):
      if (fetch not in (
         SQLite3Engine.FETCH.RAW,
         SQLite3Engine.FETCH.ONE,
         SQLite3Engine.FETCH.ALL,
      )):
         fetch = SQLite3Engine.FETCH.RAW
      
      result = None
      error = SQLite3Engine.ERROR.NONE
      
      try:
         result = self.cursor.execute(query, *args, **kwargs)
         
         if (commit):
            try:
               self.connection.commit()
            except:
               error |= SQLite3Engine.ERROR.COMMIT
         
         if ((fetch != SQLite3Engine.FETCH.RAW) and result):
            try:
               result = (result.fetchone()
                  if (fetch == SQLite3Engine.FETCH.ONE)
                  else (result.fetchall()
                     if (fetch == SQLite3Engine.FETCH.ALL)
                     else
                     result
                  )
               )
            except:
               error |= SQLite3Engine.ERROR.FETCH
      except:
         result = None
         error |= SQLite3Engine.ERROR.EXECUTION
      
      if (errorstatus):
         result = (result, error,)
      
      return result
