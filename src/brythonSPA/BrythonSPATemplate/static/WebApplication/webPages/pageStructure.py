from browser import document, window, timer

import WebApplication as App

jquery = window.jQuery

class PageStructure:
   identifier = None
   loaded = None
   
   retries = None
   retryTimer = None
   
   controlBarIdentifier = None
   controlBarSelectionIdentifier = None
   controlBarSelectedIdentifier = None
   contentBlockIdentifier = None
   informationModal = None
   informationModalAutocloseTimer = None
   informationModalHeaderIdentifier = None
   informationModalBodyIdentifier = None
   informationModalFooterIdentifier = None
   
   def start ():
      App.webPages.AppStarter.start()
      
      '''
      App.webInterface.Activator.tabs = {
         # 'default' : 'default-tabname',
         # 'tabname' : exec_function(event),
         # 'tabname' : [exit_function(event), enter_function(event),],
         # 'tabname' : {
         #    'default' : 'default-subtabname',
         #    'subtabname' : exec_function(event),
         #    'subtabname' : [exit_function(event), enter_function(event),],
         # },
      }
      App.webInterface.Activator.hiddenTabs = {
         # 'tabname' : None,
         # 'tabname' : {
         #    'subtabname' : None,
         # },
      }
      '''
      
      PageStructure.loaded = False
      PageStructure.identifier = '#main-div'
      
      PageStructure.retries = 0
      
      PageStructure.controlbarIdentifier = '.controlbar-strip'
      PageStructure.controlbarSelectionIdentifier = '.controlbar-select-btn'
      PageStructure.contentBlockIdentifier = (
         '.content-strip .content-strip-container .content-block'
      )
      PageStructure.controlbarSelectedIdentifier = (
         '.controlbar-select-item:selected'
      )
      PageStructure.informationModalHeaderIdentifier = (
         '.information-modal-header'
      )
      PageStructure.informationModalBodyIdentifier = (
         '.information-modal-body'
      )
      PageStructure.informationModalFooterIdentifier = (
         '.information-modal-footer'
      )
      
      App.Configuration.appUrl = jquery(
         "{0} .init-data #app-url".format(PageStructure.identifier,)
      ).text()
      App.Configuration.staticUrl = jquery(
         "{0} .init-data #static-url".format(PageStructure.identifier,)
      ).text()
   
   def initialize ():
      pendingTab = jquery(
         "{0} .init-data #tab-name".format(PageStructure.identifier,)
      ).text() or 'default'
      pendingSubTab = jquery(
         "{0} .init-data #subtab-name".format(PageStructure.identifier,)
      ).text() or 'default'
      
      jquery(
         "{0} .init-data".format(PageStructure.identifier,)
      ).remove()
      
      if (
            (pendingTab != 'default')
            and (pendingTab not in App.webInterface.Activator.getTabList(True))
         ):
         pendingTab = 'default'
         pendingSubTab = 'default'
      
      PageStructure.load()
      App.webInterface.Activator.activate(
         event=None,
         tab=pendingTab,
         subtab=pendingSubTab,
      )
   
   def updateTabInfo (autoload=False):
      if ((not autoload) and (not PageStructure.loaded)):
         return None
      else:
         PageStructure.load()
      
      jquery(".navbar-tab-field.tab-full-name").text(
         (App.webInterface.Activator.activeTab or '-').capitalize(),
      )
      jquery(".navbar-tab-field.tab-short-name").text(
         (App.webInterface.Activator.activeTab or '-').capitalize()[0],
      )
      jquery(".navbar-tab-field.subtab-full-name").text(
         (App.webInterface.Activator.activeSubTab or '-').capitalize(),
      )
      jquery(".navbar-tab-field.subtab-short-name").text(
         (App.webInterface.Activator.activeSubTab or '-').capitalize()[0],
      )
      
      jquery(".activator-active").removeClass("activator-active")
      
      if (App.webInterface.Activator.activeTab != None):
         jquery(
            ".activator-item-{0}".format(App.webInterface.Activator.activeTab)
         ).addClass("activator-active")
      
      if (App.webInterface.Activator.activeSubTab != None):
         jquery(
            ".activator-item-{0}-{1}".format(
               App.webInterface.Activator.activeTab,
               App.webInterface.Activator.activeSubTab,
            )
         ).addClass("activator-active")
   
   def updateTitle (title=None, autoload=False):
      if ((not autoload) and (not PageStructure.loaded)):
         return None
      else:
         PageStructure.load()
      
      if (title == None):
         title = '{0} - {1} | {2}'.format(
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
      
      document.title = title
      jquery('.navbar-offcanvas-title').text(
         title,
      )
   
   def load (*args, **kwargs):
      if (App.Configuration.pageStructureType == 'sidebar'):
         return PageStructure.loadSidebar(*args, **kwargs)
      elif (App.Configuration.pageStructureType == 'topbar'):
         return PageStructure.loadTopbar(*args, **kwargs)
      
      return None
   
   def loadSidebar (force=False):
      if ((not force) and (PageStructure.loaded)):
         return None
      
      offcanvasStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.strip',
      )
      accordionItem_nosubtab = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item.nosubtab',
      )
      accordionItem = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item',
      )
      accordionItem_subtab = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item.subtab',
      )
      navbarStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.navbar.strip',
      )
      controlbarSelectionItem = App.webInterface.TemplateManager.getTemplate(
         'layout.controlbar.selectionitem',
      )
      controlbarDashboardItem = App.webInterface.TemplateManager.getTemplate(
         'layout.controlbar.dashboard.item',
      )
      controlbarStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.controlbar.strip',
      )
      sidebarItem_nosubtab = App.webInterface.TemplateManager.getTemplate(
         'layout.sidebar.item.nosubtab',
      )
      sidebarItem = App.webInterface.TemplateManager.getTemplate(
         'layout.sidebar.item',
      )
      sidebarItem_subtab = App.webInterface.TemplateManager.getTemplate(
         'layout.sidebar.item.subtab',
      )
      contentStrip_sidebar = App.webInterface.TemplateManager.getTemplate(
         'layout.content.strip.sidebar',
      )
      informationModalStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.information.modal.strip',
      )
      informationModal_title = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.title',
         )
      )
      informationModal_closebutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.closebutton',
         )
      )
      informationModal_selectionbutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.selectionbutton',
         )
      )
      
      try:
         timer.clear_timeout(PageStructure.retryTimer)
         PageStructure.retryTimer = None
      except:
         PageStructure.retryTimer = None
      
      if (None in (
            offcanvasStrip, accordionItem_nosubtab, accordionItem,
            accordionItem_subtab,
            navbarStrip,
            controlbarSelectionItem, controlbarDashboardItem,
            controlbarStrip,
            sidebarItem_nosubtab, sidebarItem,
            sidebarItem_subtab,
            contentStrip_sidebar,
            informationModalStrip,
            informationModal_title,
            informationModal_closebutton, informationModal_selectionbutton,
         )):
         if (PageStructure.retries < App.Configuration.failureMaxRetries):
            PageStructure.retries += 1
            
            PageStructure.retryTimer = timer.set_timeout(
               PageStructure.loadSidebar,
               App.Configuration.failureRefreshInterval,
            )
            
            return None
         else:
            PageStructure.retries = 0
            return None
         
         return None
      else:
         PageStructure.retries = 0
      
      offcanvasbody = []
      sidebarbody = []
      
      for tab in App.webInterface.Activator.getTabList():
         if (
               (
                  type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                     'tuple', 'list',
                  )
               )
               or callable(App.webInterface.Activator.tabs.get(tab))
            ):
            offcanvasbody.append(
               App.webInterface.TemplateManager.render(
                  accordionItem_nosubtab,
                  tabname=tab,
                  ctabname=tab.capitalize(),
               )
            )
            sidebarbody.append(
               App.webInterface.TemplateManager.render(
                  sidebarItem_nosubtab,
                  tabimageurl='{0}{1}'.format(
                     App.Configuration.staticUrl,
                     'Images/test.jpg',
                  ),
                  tabname=tab,
                  ctabname=tab.capitalize(),
                  cshorttabname=tab.capitalize()[0],
               )
            )
         elif (
               type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                  'dict',
               )
            ):
            offcanvassubtabitems = []
            sidebarsubtabitems = []
            
            for subtab in App.webInterface.Activator.getSubTabList(tab):
               offcanvassubtabitems.append(
                  App.webInterface.TemplateManager.render(
                     accordionItem_subtab,
                     tabname=tab,
                     subtabname=subtab,
                     csubtabname=subtab.capitalize(),
                  )
               )
               sidebarsubtabitems.append(
                  App.webInterface.TemplateManager.render(
                     sidebarItem_subtab,
                     tabname=tab,
                     subtabname=subtab,
                     csubtabname=subtab.capitalize(),
                  )
               )
            
            offcanvassubtabitems = ''.join(offcanvassubtabitems)
            sidebarsubtabitems = ''.join(sidebarsubtabitems)
            
            offcanvasbody.append(
               App.webInterface.TemplateManager.render(
                  accordionItem,
                  tabname=tab,
                  ctabname=tab.capitalize(),
                  subtabitems=offcanvassubtabitems,
               )
            )
            sidebarbody.append(
               App.webInterface.TemplateManager.render(
                  sidebarItem,
                  tabimageurl='{0}{1}'.format(
                     App.Configuration.staticUrl,
                     'Images/test.jpg',
                  ),
                  tabname=tab,
                  ctabname=tab.capitalize(),
                  cshorttabname=tab.capitalize()[0],
                  subtabitems=sidebarsubtabitems,
               )
            )
      
      offcanvasbody = ''.join(offcanvasbody)
      sidebarbody = ''.join(sidebarbody)
      
      jquery(PageStructure.identifier).html(
         ''.join((
            App.webInterface.TemplateManager.render(
               offcanvasStrip,
               title='{0} - {1}'.format(
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
               body=offcanvasbody,
            ),
            App.webInterface.TemplateManager.render(
               navbarStrip,
               tabname='-',
               subtabname='-',
               brandimageurl='{0}{1}'.format(
                  App.Configuration.staticUrl,
                  App.Configuration.brandImageUrl,
               ),
               rtoptabitems='',
            ),
            App.webInterface.TemplateManager.render(
               controlbarStrip,
               controlbaritems=App.webInterface.TemplateManager.render(
                  controlbarDashboardItem,
                  selectionitems='',
               ),
            ),
            App.webInterface.TemplateManager.render(
               contentStrip_sidebar,
               sidebaritems=sidebarbody,
               body='So now, the body has been loaded as well.',
               # Replace it with empty string or some load-time message maybe.
            ),
            App.webInterface.TemplateManager.render(
               informationModalStrip,
               header='', body='', selectionitems='',
            ),
         ))
      )
      
      return PageStructure.bindTabs()
   
   def loadTopbar (force=False):
      if ((not force) and (PageStructure.loaded)):
         return None
      
      offcanvasStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.strip',
      )
      accordionItem_nosubtab = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item.nosubtab',
      )
      accordionItem = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item',
      )
      accordionItem_subtab = App.webInterface.TemplateManager.getTemplate(
         'layout.offcanvas.accordion.item.subtab',
      )
      navbarStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.navbar.strip',
      )
      navbarLoginButton = App.webInterface.TemplateManager.getTemplate(
         'layout.navbar.loginbutton',
      )
      topbarStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.topbar.strip',
      )
      topbarItem_nosubtab = App.webInterface.TemplateManager.getTemplate(
         'layout.topbar.item.nosubtab',
      )
      topbarItem = App.webInterface.TemplateManager.getTemplate(
         'layout.topbar.item',
      )
      topbarItem_subtab = App.webInterface.TemplateManager.getTemplate(
         'layout.topbar.item.subtab',
      )
      contentStrip_nosidebar = App.webInterface.TemplateManager.getTemplate(
         'layout.content.strip.nosidebar',
      )
      informationModalStrip = App.webInterface.TemplateManager.getTemplate(
         'layout.information.modal.strip',
      )
      informationModal_title = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.title',
         )
      )
      informationModal_closebutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.closebutton',
         )
      )
      informationModal_selectionbutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.selectionbutton',
         )
      )
      
      try:
         timer.clear_timeout(PageStructure.retryTimer)
         PageStructure.retryTimer = None
      except:
         PageStructure.retryTimer = None
      
      if (None in (
            offcanvasStrip, accordionItem_nosubtab, accordionItem,
            accordionItem_subtab,
            navbarStrip, navbarLoginButton,
            topbarStrip, topbarItem_nosubtab, topbarItem,
            topbarItem_subtab,
            contentStrip_nosidebar,
            informationModalStrip,
            informationModal_title,
            informationModal_closebutton, informationModal_selectionbutton,
         )):
         if (PageStructure.retries < App.Configuration.failureMaxRetries):
            PageStructure.retries += 1
            
            PageStructure.retryTimer = timer.set_timeout(
               PageStructure.loadTopbar,
               App.Configuration.failureRefreshInterval,
            )
            
            return None
         else:
            PageStructure.retries = 0
            return None
         
         return None
      else:
         PageStructure.retries = 0
      
      offcanvasbody = []
      topbarbody = []
      
      for tab in App.webInterface.Activator.getTabList():
         if (
               (
                  type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                     'tuple', 'list',
                  )
               )
               or callable(App.webInterface.Activator.tabs.get(tab))
            ):
            offcanvasbody.append(
               App.webInterface.TemplateManager.render(
                  accordionItem_nosubtab,
                  tabname=tab,
                  ctabname=tab.capitalize(),
               )
            )
            topbarbody.append(
               App.webInterface.TemplateManager.render(
                  topbarItem_nosubtab,
                  tabname=tab,
                  ctabname=tab.capitalize(),
               )
            )
         elif (
               type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                  'dict',
               )
            ):
            offcanvassubtabitems = []
            topbarsubtabitems = []
            
            for subtab in App.webInterface.Activator.getSubTabList(tab):
               offcanvassubtabitems.append(
                  App.webInterface.TemplateManager.render(
                     accordionItem_subtab,
                     tabname=tab,
                     subtabname=subtab,
                     csubtabname=subtab.capitalize(),
                  )
               )
               topbarsubtabitems.append(
                  App.webInterface.TemplateManager.render(
                     topbarItem_subtab,
                     tabname=tab,
                     subtabname=subtab,
                     csubtabname=subtab.capitalize(),
                  )
               )
            
            offcanvassubtabitems = ''.join(offcanvassubtabitems)
            topbarsubtabitems = ''.join(topbarsubtabitems)
            
            offcanvasbody.append(
               App.webInterface.TemplateManager.render(
                  accordionItem,
                  tabname=tab,
                  ctabname=tab.capitalize(),
                  subtabitems=offcanvassubtabitems,
               )
            )
            topbarbody.append(
               App.webInterface.TemplateManager.render(
                  topbarItem,
                  tabname=tab,
                  ctabname=tab.capitalize(),
                  subtabitems=topbarsubtabitems,
               )
            )
      
      offcanvasbody = ''.join(offcanvasbody)
      topbarbody = ''.join(topbarbody)
      
      jquery(PageStructure.identifier).html(
         ''.join((
            App.webInterface.TemplateManager.render(
               offcanvasStrip,
               title='{0} - {1}'.format(
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
               body=offcanvasbody,
            ),
            App.webInterface.TemplateManager.render(
               navbarStrip,
               tabname='-',
               subtabname='-',
               brandimageurl='{0}{1}'.format(
                  App.Configuration.staticUrl,
                  App.Configuration.brandImageUrl,
               ),
               rtoptabitems=navbarLoginButton,
            ),
            App.webInterface.TemplateManager.render(
               topbarStrip,
               body=topbarbody,
            ),
            App.webInterface.TemplateManager.render(
               contentStrip_nosidebar,
               body='So now, the body has been loaded as well.',
            ),
            App.webInterface.TemplateManager.render(
               informationModalStrip,
               header='', body='', selectionitems='',
            ),
         ))
      )
      
      return PageStructure.bindTabs()
   
   def bindTabs ():
      '''
      jquery('.navbar-login-button').on(
         'click',
         (lambda event=None: print('login')),
      )'''
      
      for tab in App.webInterface.Activator.getTabList(True):
         if (
               (
                  type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                     'tuple', 'list',
                  )
               )
               or callable(App.webInterface.Activator.tabs.get(tab))
            ):
            jquery('.activator-{0}-button'.format(tab)).on(
               'click',
               (
                  lambda event=None, tab=tab: (
                     App.webInterface.Activator.activate(event, tab)
                  )
               ),
            )
         elif (
               type(App.webInterface.Activator.tabs.get(tab)).__name__ in (
                  'dict',
               )
            ):
            for subtab in App.webInterface.Activator.getSubTabList(tab, True):
               jquery('.activator-{0}-{1}-button'.format(tab, subtab)).on(
                  'click',
                  (
                     lambda event=None, tab=tab, subtab=subtab: (
                        App.webInterface.Activator.activate(event, tab, subtab)
                     )
                  ),
               )
      
      PageStructure.informationModal = window.bootstrap.Modal.new(
         jquery('.information-modal-strip')[0]
      )
      
      PageStructure.loaded = True
      
      return True
   
   def disableControlbar ():
      jquery(PageStructure.controlbarSelectionIdentifier).off()
      jquery(PageStructure.controlbarSelectionIdentifier).html('')
      
      PageStructure.disableControlbarBack()
      
      jquery(PageStructure.controlbarIdentifier).addClass(
         'd-none'
      )
   
   def enableControlbar (selectionitems=None, changehandler=None):
      if (selectionitems):
         jquery(PageStructure.controlbarSelectionIdentifier).html(
            selectionitems
         )
      
      if (callable(changehandler)):
         jquery(PageStructure.controlbarSelectionIdentifier).on(
            'change',
            changehandler,
         )
      
      jquery(PageStructure.controlbarIdentifier).removeClass(
         'd-none'
      )
   
   def disableControlbarBack ():
      jquery(PageStructure.controlbarIdentifier + ' .back-button').off()
      jquery(PageStructure.controlbarIdentifier + ' .back-button').addClass(
         'd-none'
      )
   
   def enableControlbarBack (backhandler=None):
      jquery(PageStructure.controlbarIdentifier + ' .back-button').removeClass(
         'd-none'
      )
      
      if (callable(backhandler)):
         jquery(PageStructure.controlbarIdentifier + ' .back-button').on(
            'click',
            backhandler,
         )
   
   def enableModal (title=None, closebutton=None, body=None,
         selectionitems=None, show=None, autocloseTimeout=None,
      ):
      informationModal_title = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.title',
         )
      )
      informationModal_closebutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.closebutton',
         )
      )
      
      if (None in (
            informationModal_title, informationModal_closebutton,
         )):
         return None
      
      header = []
      
      if (title):
         header.append(
            App.webInterface.TemplateManager.render(
               informationModal_title,
               title=title,
            )
         )
      
      if (closebutton):
         header.append(
            App.webInterface.TemplateManager.render(
               informationModal_closebutton,
            )
         )
      
      header = ''.join(header)
      
      if (header):
         jquery(PageStructure.informationModalHeaderIdentifier).html(header)
      
      if (body):
         jquery(PageStructure.informationModalBodyIdentifier).html(body)
      
      if (selectionitems):
         jquery(PageStructure.informationModalFooterIdentifier).html(
            selectionitems
         )
      
      if (show):
         PageStructure.showModal(autocloseTimeout=autocloseTimeout)
   
   def showModal (autocloseTimeout=None):
      try:
         timer.clear_timeout(PageStructure.informationModalAutocloseTimer)
         PageStructure.informationModalAutocloseTimer = None
      except:
         PageStructure.informationModalAutocloseTimer = None
      
      if (not PageStructure.informationModal):
         return None
      
      if (type(autocloseTimeout).__name__ == 'int'):
         PageStructure.retryTimer = timer.set_timeout(
            PageStructure.closeModal,
            autocloseTimeout,
         )
      
      PageStructure.informationModal.show()
   
   def closeModal (event=None):
      try:
         timer.clear_timeout(PageStructure.informationModalAutocloseTimer)
         PageStructure.informationModalAutocloseTimer = None
      except:
         PageStructure.informationModalAutocloseTimer = None
      
      if (not PageStructure.informationModal):
         return None
      
      PageStructure.informationModal.hide()
      
      jquery(PageStructure.informationModalHeaderIdentifier).html('')
      jquery(PageStructure.informationModalBodyIdentifier).html('')
      jquery(PageStructure.informationModalFooterIdentifier).html('')
   
   def showConnectionError (body=None, reloadFunction=None):
      informationModal_selectionbutton = (
         App.webInterface.TemplateManager.getTemplate(
            'layout.information.modal.selectionbutton',
         )
      )
      
      App.webPages.PageStructure.enableModal(
         title='Connection Error!', closebutton=True,
         body=(body
            or ('Can\'t connect to internet!<BR /><BR />'
                  + 'Please check your internet connection!'
               )
         ),
         selectionitems=''.join((
            (App.webInterface.TemplateManager.render(
                  informationModal_selectionbutton,
                  color='outline-success',
                  name='reload',
                  cname='Reload',
               )
               if (reloadFunction and callable(reloadFunction))
               else ''
            ),
            App.webInterface.TemplateManager.render(
               informationModal_selectionbutton,
               color='outline-danger',
               name='close',
               cname='Close',
            ),
         )),
         show=True, autocloseTimeout=40000,
      )
      
      if (reloadFunction and callable(reloadFunction)):
         jquery('.information-modal-selection-reload-button').on(
            'click',
            (lambda event=None, *args, **kwargs: (
               (App.webPages.PageStructure.closeModal() and False)
               or reloadFunction()
            )),
         )
      
      jquery('.information-modal-selection-close-button').on(
         'click',
         (lambda event=None, *args, **kwargs: (
            App.webPages.PageStructure.closeModal()
         )),
      )
