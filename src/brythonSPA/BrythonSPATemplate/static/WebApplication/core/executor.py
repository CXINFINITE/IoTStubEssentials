import WebApplication as App

class Executor:
   def web_executor ():
      App.webPages.PageStructure.start()
      
      App.webInterface.ConnectionManager.start()
      App.webInterface.StateManager.start()
      
      App.webPages.PageStructure.initialize()
