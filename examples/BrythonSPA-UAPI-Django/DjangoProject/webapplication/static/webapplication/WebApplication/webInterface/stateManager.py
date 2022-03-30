from browser import document, window

import WebApplication as App

jquery = window.jQuery

class StateManager:
   popStateEnabled = None
   pageUnloadEnabled = None
   
   stateOperators = None
   
   def start ():
      StateManager.popStateEnabled = True
      StateManager.pageUnloadEnabled = False
      
      StateManager.stateOperators = {
         'push': window.history.pushState,
         'replace': window.history.replaceState,
      }
      
      window.history.replaceState(
         {
            'tab' : None,
            'subtab' : None,
            'loggedin' : False,
            'title': '{0} - {1}'.format(
               App.Configuration.appName,
               (App.Configuration.applicationName
                  if (not App.Configuration.subApplicationName)
                  else (
                     '{1} {0}'.format(
                        App.Configuration.applicationName,
                        App.Configuration.subApplicationName,
                     )
                  )
               ),
            ),
         },
         '{0} - {1}'.format(
            App.Configuration.appName,
            (App.Configuration.applicationName
               if (not App.Configuration.subApplicationName)
               else (
                  '{1} {0}'.format(
                     App.Configuration.applicationName,
                     App.Configuration.subApplicationName,
                  )
               )
            ),
         ),
         '{0}'.format(
            App.Configuration.appUrl,
         ),
      )
      
      window.onpopstate = StateManager.onPopState
      window.onbeforeunload = StateManager.onBeforeUnload
   
   def disablePopState ():
      StateManager.popStateEnabled = False
   
   def enablePageUnload ():
      StateManager.pageUnloadEnabled = True
   
   def unloadPage (link):
      StateManager.pageUnloadEnabled = False
      window.onbeforeunload = None
      window.location.href = link
      window.onbeforeunload = StateManager.onBeforeUnload
   
   def replaceState (*args, **kwargs):
      StateManager.operateState('replace', *args, **kwargs)
   
   def pushState (*args, **kwargs):
      StateManager.operateState('push', *args, **kwargs)
   
   def operateState (operation='push', state=None):
      if (operation not in StateManager.stateOperators.keys()):
         return None
      
      operableState = dict()
      
      if (state != None):
         operableState['title'] = state.get('title')
         operableState['tab'] = state.get('tab')
         operableState['subtab'] = (
            state.get('subtab')
            if (state.get('tab') != None)
            else None
         )
         operableState['loggedin'] = state.get('loggedin')
      else:
         operableState['title'] = document.title or (
            '{0} - {1} | {2}'.format(
               App.Configuration.appName,
               (App.Configuration.applicationName
                  if (not App.Configuration.subApplicationName)
                  else (
                     '{1} {0}'.format(
                        App.Configuration.applicationName,
                        App.Configuration.subApplicationName,
                     )
                  )
               ),
               (
                  App.webInterface.Activator.activeTab.capitalize()
                  + (
                     ' > {0}'.format(
                        App.webInterface.Activator.activeSubTab.capitalize(),
                     )
                     if (App.webInterface.Activator.activeSubTab != None)
                     else ''
                  )
               ),
            )
         )
         operableState['tab'] = App.webInterface.Activator.activeTab
         operableState['subtab'] = App.webInterface.Activator.activeSubTab
         operableState['loggedin'] = App.Configuration.loggedIn
      
      StateManager.stateOperators[operation](
         {
            'tab' : operableState.get('tab'),
            'subtab' : operableState.get('subtab'),
            'loggedin' : operableState.get('loggedin'),
            'title' : operableState.get('title'),
         },
         operableState.get('title'),
         '{0}'.format(
            App.Configuration.appUrl
            + (
               '{0}/'.format(
                  operableState.get('tab')
                  + (
                     '/{0}'.format(
                        operableState.get('subtab'),
                     )
                     if (operableState.get('subtab') != None)
                     else ''
                  )
               )
               if (operableState.get('tab') != None)
               else ''
            ),
         ),
      )
      
      # document.title = '{0}'.format(title.capitalize(),)
   
   def onPopState (event):
      try:
         state = event['state'].to_dict()
      except:
         return None
      
      if (state != None and StateManager.popStateEnabled):
         App.webInterface.Activator.activate(
            tab=state.get('tab'),
            subtab=state.get('subtab'),
            popStateEvent=True,
         )
      elif (state != None and (not StateManager.popStateEnabled)):
         StateManager.popStateEnabled = True
         # StateManager.replaceState(state)
         # StateManager.pushState()
         StateManager.replaceState()
      
      return None
   
   def onBeforeUnload (event):
      if (
            (not StateManager.pageUnloadEnabled)
            and (not App.webInterface.Activator.deactivate())
         ):
         event['returnValue'] = 'Are you sure you want to exit?'
         event.preventDefault()
         
         return 'Are you sure you want to exit?'
      else:
         StateManager.pageUnloadEnabled = False
