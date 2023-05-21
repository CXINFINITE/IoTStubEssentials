import genericflaskwebapp as app

class API:
   class DataBase:
      SQLite3 = 1
   
   class Model:
      ModelsV1 = 1
   
   def database_start (database, path):
      if (app.database.engine):
         app.database.engine.close()
      
      if (not (database or path)):
         return None
      
      if (database == API.DataBase.SQLite3):
         from .engines import sqlite3engine
         from .modelenginebridges import sqlite3bridge
         
         app.database.engine = sqlite3engine.SQLite3Engine(path)
         app.database.modelenginebridge = sqlite3bridge
         
         from .models import modelsv1
         
         app.database.models = modelsv1
      
      return True
   
   def model_start (model):
      if (not app.database.engine):
         return False
      
      if (model == API.Model.ModelsV1):
         from .models import modelsv1
         
         app.database.models = modelsv1
      
      return True
   
   def close ():
      if (app.database.engine):
         app.database.engine.close()
