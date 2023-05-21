import genericflaskwebapp as app

class Model1 (app.database.modelenginebridge.models.Model):
   modelname = 'Model1'
   
   fieldname = app.database.modelenginebridge.models.Fields.Int(
      main=True,
      autoincrement=True,
   )
   
   field2 = app.database.modelenginebridge.models.Fields.Str(
      main=False,
      unique=True,
      notnone=True,
   )
   
   field3 = app.database.modelenginebridge.models.Fields.Str(
      fieldname='myfield',
      main=False,
      unique=True,
      notnone=True,
   )
   
   def _set_field2 (self, field2=None):
      if (not fieldname):
         fieldname = ''
      
      return (str(fieldname).strip())
