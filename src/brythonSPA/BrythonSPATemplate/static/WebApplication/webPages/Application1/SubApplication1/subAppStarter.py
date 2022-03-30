import WebApplication as App

class SubAppStarter:
   def start ():
      App.Configuration.subApplicationName = 'SubApplication1'
      App.Configuration.pageStructureType = 'sidebar' # or 'topbar'
      
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
         'tab1' : [
            App.webPages.Application1.SubApplication1.Tab1.entry,
            App.webPages.Application1.SubApplication1.Tab1.exit,
         ],
      }
      App.webInterface.Activator.hiddenTabs = {
         # 'tabname' : None,
         # 'tabname' : {
         #    'subtabname' : None,
         # },
         'login' : None,
      }
      # For illustration only.
      # Add your own tabs.
      # Each entry / exit event must return either True or False to mark
      # success or failue. Activator depends on these values.
