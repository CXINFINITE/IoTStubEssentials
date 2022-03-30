import WebApplication as App

class Activator:
   tabs = {}
   hiddenTabs = {}
   
   activeTab = None
   activeSubTab = None
   
   def getTabList (listhidden=False):
      return [
         tab
         for tab in Activator.tabs.keys()
         if (
               (tab != None) and (tab != '') and (tab != 'default')
               and (
                  (
                     True
                     if (tab not in Activator.hiddenTabs.keys())
                     else (
                        True
                        if (
                              type(Activator.hiddenTabs.get(tab)).__name__ in (
                                 'dict',
                              )
                           )
                        else False
                     )
                  )
                  if (not listhidden)
                  else True
               )
            )
      ]
   
   def getSubTabList (tab, listhidden=False):
      if (tab in Activator.getTabList(listhidden=listhidden)):
         return [
            subtab
            for subtab in Activator.tabs.get(tab).keys()
            if (
                  (subtab != None) and (subtab != '')
                  and (subtab != 'default')
                  and (
                     (
                        False
                        if (
                              (tab in Activator.hiddenTabs.keys())
                              and (Activator.hiddenTabs.get(tab) == None)
                           )
                        else (
                           (subtab not in Activator.hiddenTabs.get(tab).keys())
                           if (
                                 (tab in Activator.hiddenTabs.keys())
                                 and (type(
                                       Activator.hiddenTabs.get(tab)
                                    ).__name__ in (
                                       'dict',
                                    )
                                 )
                              )
                           else True
                        )
                     )
                     if (not listhidden)
                     else True
                  )
               )
         ]
      
      return []
   
   def deactivate ():
      proceed = True
      
      try:
         if (
               (Activator.activeTab != None)
               and (Activator.activeSubTab == None)
            ):
            if (
                  type(
                     Activator.tabs.get(Activator.activeTab)
                  ).__name__ in ('tuple', 'list',)
                  and callable(Activator.tabs.get(Activator.activeTab)[0])
               ):
               proceed = Activator.tabs.get(Activator.activeTab)[0]()
         elif (
               (Activator.activeTab != None)
               and (Activator.activeSubTab != None)
            ):
            if (
                  (
                     type(
                        Activator.tabs.get(Activator.activeTab)
                     ).__name__ in ('dict',)
                  )
                  and (
                     type(
                        Activator.tabs.get(Activator.activeTab).get(
                           Activator.activeSubTab,
                        )
                     ).__name__ in ('tuple', 'list',)
                  )
                  and callable(
                     Activator.tabs.get(Activator.activeTab).get(
                        Activator.activeSubTab,
                     )[0]
                  )
               ):
               proceed = Activator.tabs.get(Activator.activeTab).get(
                  Activator.activeSubTab,
               )[0]()
         else:
            proceed = True
      except:
         proceed = True
      
      return proceed
   
   def activate (event=None, tab=None, subtab=None, popStateEvent=False,
         force=False, skipdeactivation=False,
      ):
      try:
         if (tab in (None, 'default',)):
            tab = Activator.tabs.get('default')
            subtab = None
         
         if (tab not in Activator.tabs.keys()):
            return None
         
         if (
               callable(Activator.tabs.get(tab))
               or (
                  type(Activator.tabs.get(tab)).__name__ in (
                     'tuple', 'list',
                  )
               )
            ):
            subtab = None
         else:
            if (subtab in (None, 'default',)):
               subtab = Activator.tabs.get(tab).get('default')
            
            if (subtab not in Activator.tabs.get(tab).keys()):
               return None
            
            if (not (
                  callable(Activator.tabs.get(tab).get(subtab))
                  or (
                     type(Activator.tabs.get(tab).get(subtab)).__name__ in (
                        'tuple', 'list',
                     )
                  )
               )):
               return None
      except:
         return None
      
      if (
            (tab != Activator.activeTab)
            or (
               (tab == Activator.activeTab)
               and (subtab != Activator.activeSubTab)
            )
            or (force)
         ):
         
         if ((not skipdeactivation) and (not Activator.deactivate())):
            App.webInterface.StateManager.replaceState()
            return None
         
         activated = False
         
         try:
            if (callable(Activator.tabs.get(tab))):
               activated = Activator.tabs.get(tab)(event)
            elif (
                  (
                     type(
                        Activator.tabs.get(tab)
                     ).__name__ in ('tuple', 'list',)
                  )
                  and callable(Activator.tabs.get(tab)[-1])
               ):
               activated = Activator.tabs.get(tab)[-1](event)
            elif (
                  (
                     type(
                        Activator.tabs.get(tab)
                     ).__name__ in ('dict',)
                  )
                  and callable(Activator.tabs.get(tab).get(subtab))
               ):
               activated = Activator.tabs.get(tab).get(subtab)(event)
            elif (
                  (
                     type(
                        Activator.tabs.get(tab)
                     ).__name__ in ('dict',)
                  )
                  and (
                     type(Activator.tabs.get(tab).get(subtab)).__name__ in (
                        'tuple', 'list',
                     )
                  )
                  and callable(Activator.tabs.get(tab).get(subtab)[-1])
               ):
               activated = Activator.tabs.get(tab).get(subtab)[-1](event)
         except:
            activated = False
         
         if (activated):
            Activator.activeTab = tab
            Activator.activeSubTab = subtab
            
            App.webPages.PageStructure.updateTabInfo()
            
            if (not popStateEvent):
               App.webInterface.StateManager.pushState()
            else:
               App.webInterface.StateManager.replaceState()
         else:
            if ((not force) and (not skipdeactivation)):
               Activator.activate(
                  event=event,
                  tab=Activator.activeTab, subtab=Activator.activeSubTab,
                  popStateEvent=True, force=True, skipdeactivation=True,
               )
               return None
            else:
               App.webPages.PageStructure.enableModal(
                  title='Tab activation error!', closebutton=True,
                  body=(
                     "Unable to activate '{0}' tab.".format(
                        (
                           tab.capitalize()
                           if (not subtab)
                           else '{0} > {1}'.format(
                              tab.capitalize(), subtab.capitalize(),
                           )
                        ),
                     )
                     + '<BR /><BR />Please check your internet connection for '
                     + 'it might be causing issue, though we can\'t say it '
                     + 'for sure.'
                  ),
                  show=True, autocloseTimeout=30000,
               )
            App.webInterface.StateManager.replaceState()
         
         return None
      else:
         return None
