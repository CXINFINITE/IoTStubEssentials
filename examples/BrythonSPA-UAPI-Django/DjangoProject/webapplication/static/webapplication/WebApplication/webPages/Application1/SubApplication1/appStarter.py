import WebApplication as App

class AppStarter:
   def start ():
      App.Configuration.applicationName = 'Application1'
      App.Configuration.loggedIn = True
      
      App.webPages.Application1.SubAppStarter.start()
