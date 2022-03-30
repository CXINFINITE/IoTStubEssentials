from browser import window, timer
from javascript import JSON

import WebApplication as App

jquery = window.jQuery

class ConnectionManager:
   connectionType = None
   
   retries = None
   retryTimer = None
   
   class DataHandler:
      def __init__ (self, data=None, callback=None):
         self.data = data
         self.callback = callback
      
      def responseHandler (self, data):
         self.data = data
         
         if (self.callback):
            self.callback(data)
         
         return None
      
      def dataVerificationLoop (self, maxLoops=10000):
         currentLoops = 0
         
         while (self.data == None):
            currentLoops += 1
            if (currentLoops >= maxLoops):
               break
         
         return self.data
   
   def start ():
      ConnectionManager.retries = 0
      
      ConnectionManager.connectionType = 'ajax'
   
   def ajaxResponseHandler (callback, data=None, textStatus=None):
      try:
         data = data.to_dict()
         if (not data.get('status')):
            data = None
      except:
         data = None
      
      if (not data):
         return callback(App.Configuration.apiErrorData.copy())
      else:
         return callback(data)
   
   def ajaxRequestHandler (url, data, callback,
         blocking, timeout, method, caching,
      ):
      jquery.ajax({
         'url': url,
         'method': method,
         'cache': caching,
         'async': (not blocking),
         'timeout': timeout,
         'data': JSON.stringify(data),
         'contentType': 'application/json',
      }).always(
         lambda data, textStatus, *args, callback=callback: (
            ConnectionManager.ajaxResponseHandler(
               callback, data, textStatus,
            )
         )
      )
   
   def fetch (endpoint=None, data='', callback=None,
         blocking=App.Configuration.connectionBlocking,
         timeout=App.Configuration.connectionTimeout,
         method=App.Configuration.ajaxMethod,
         caching=App.Configuration.ajaxCaching,
         connectionType=None,
      ):
      if (not connectionType):
         connectionType = ConnectionManager.connectionType
      
      if (
            ((not blocking) and (not callback))
            or (callback and (not callable(callback)))
         ):
         return None
      
      if (not endpoint):
         return None
      
      if (connectionType == 'ajax'):
         dataHandler = ConnectionManager.DataHandler(callback=callback)
         ConnectionManager.ajaxRequestHandler(
            url=endpoint,
            data=data, callback=dataHandler.responseHandler,
            blocking=blocking, timeout=timeout, method=method, caching=caching,
         )
         
         dataResponse = None
         
         if (blocking):
            dataResponse = dataHandler.dataVerificationLoop()
         
         dataResponse = dataResponse or dataHandler.data
         
         if (not blocking):
            return dataResponse
         
         if (callback):
            callback(dataResponse)
            return None
         else:
            return dataResponse
      else:
         return None
