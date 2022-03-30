import WebApplication as App

class Executor:
   def web_executor ():
      App.core.UAPIManager.start()
      App.webPages.PageStructure.start()
      
      App.webInterface.ConnectionManager.start()
      App.webInterface.StateManager.start()
      
      App.webPages.PageStructure.initialize()
      App.core.UAPIManager.initialize()
