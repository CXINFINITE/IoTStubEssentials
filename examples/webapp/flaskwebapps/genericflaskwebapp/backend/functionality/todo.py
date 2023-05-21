import genericflaskwebapp as app

class ToDo:
   class ERROR:
      NONE = None
      TODO_NOTE_CREATION_FAILURE = 'Todo note creation failure'
      TODO_NOTE_DELETION_FAILURE = 'Todo note deletion failure'
      INCOMPLETE_DETAILS = 'Incomplete details'
      USERNAME_DOES_NOT_EXISTS = 'Username does not exists'
      INVALID_TODOID = 'Invalid todoid'
      TODO_DOES_NOT_EXISTS = 'Todo does not exists'
      TODOS_NOT_FOUND = 'Todos not found'
   
   def create (username, note):
      if (not username):
         return (None, ToDo.ERROR.INCOMPLETE_DETAILS)
      
      username = str(username).strip()
      note = str(note).strip()
      
      usernameexists = app.database.models.User.search_aggregate(
         select='username',
         aggregate=app.database.models.User.AGGREGATE.COUNT,
         username=username,
      )
      
      if (not usernameexists.get('username')):
         return (None, ToDo.ERROR.USERNAME_DOES_NOT_EXISTS)
      
      try:
         todo = app.database.models.ToDo(
            dbengine=app.database.engine,
            username=username,
            note=note,
         )
         todo.save()
      except:
         todo = None
      
      if (not todo):
         return (None, ToDo.ERROR.TODO_NOTE_CREATION_FAILURE)
      
      return (True, todo)
   
   def delete (username=None, todoid=None):
      if ((username or todoid) is None):
         return (None, ToDo.ERROR.INCOMPLETE_DETAILS)
      
      if (username):
         username = str(username).strip()
      
      if (todoid is not None):
         try:
            todoid = int(todoid)
         except:
            return (None, ToDo.ERROR.INVALID_TODOID)
      
      searchdata = dict()
      
      findall = False
      
      if (username):
         searchdata['username'] = username
         findall = True
      else:
         searchdata['todoid'] = todoid
      
      todos = app.database.models.ToDo.get_todos(
         **searchdata,
      )
      
      if ((not todos) and (not findall)):
         return (None, ToDo.ERROR.TODO_DOES_NOT_EXISTS)
      
      if (not todos):
         return (None, ToDo.ERROR.TODOS_NOT_FOUND)
      
      if (not findall):
         todos = [todos,]
      
      for todo in todos:
         try:
            todo.delete()
         except:
            return (None, ToDo.ERROR.TODO_NOTE_DELETION_FAILURE)
      
      return (True, ToDo.ERROR.NONE)
