import WebApplication as App

class AppStarter:
   def start ():
      App.Configuration.applicationName = 'Application2'
      App.Configuration.subApplicationName = None
      App.Configuration.loggedIn = False
      
      App.Configuration.pageStructureType = 'topbar'
      
      App.webInterface.Activator.tabs = {
         # 'default' : 'default-tabname',
         # 'tabname' : exec_function(event),
         # 'tabname' : [exit_function(event), enter_function(event),],
         # 'tabname' : {
         #    'default' : 'default-subtabname',
         #    'subtabname' : exec_function(event),
         #    'subtabname' : [exit_function(event), enter_function(event),],
         # },
         'default' : 'np',
         'np' : [
            (lambda event=None: True if (print('You leaving np?')) else True),
            (lambda event=None: True if (print('You called np?')) else True),
         ],
         'ngo' : {
            'default' : 'nko',
            'nko' : [
               (lambda event=None: True if (print('You leaving ngo, nko?')) else True),
               (lambda event=None: True if (print('You called ngo, nko?')) else True),
            ],
            'nmo' : (lambda event=None: True if (print('You called ngo, nmo?')) else True),
         },
         'login' : [
            (lambda event=None: True if (print('You leaving login?')) else True),
            (lambda event=None: True if (print('You called login?')) else True),
         ],
      }
      App.webInterface.Activator.hiddenTabs = {
         # 'tabname' : None,
         # 'tabname' : {
         #    'subtabname' : None,
         # },
         'login' : None,
      }
      # For illustrative purpose only.
