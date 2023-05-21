import genericflaskwebapp as app

class ToDo (app.database.modelenginebridge.models.Model):
   modelname = 'Todos'
   
   todoid = app.database.modelenginebridge.models.Fields.Int(
      main=True,
      autoincrement=True,
   )
   
   username = app.database.modelenginebridge.models.Fields.Str(
      notnone=True,
   )
   
   note = app.database.modelenginebridge.models.Fields.Str(
      notnone=False,
   )
   
   def _set_username (self, username=None):
      if (not username):
         username = ''
      
      return (str(username).strip())
   
   def _set_note (self, note=None):
      if (not note):
         return ''
      
      return (str(note).strip())
   
   @classmethod
   def get_todos (cls, todoid=None, username=None):
      if (not (todoid or username)):
         return None
      
      if (todoid and username):
         return None
      
      searchdata = dict()
      if (username):
         searchdata['username'] = str(username).strip()
      else:
         searchdata['todoid'] = int(todoid)
      
      todos = cls.find(
         findall=(
            True
            if (username)
            else
            False
         ),
         **searchdata,
      )
      
      if (todos):
         return todos
      
      return None
