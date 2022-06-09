import WebApplication as App

class UAPIManager:
   endpoints = None
   endpointMapping = None
   apicodes = None
   
   apiUpdateRequestActive = None
   
   def start ():
      UAPIManager.endpointMapping = {
         'ajax': -1,
         'websocket': 0,
      }
      UAPIManager.endpoints = [None for _ in UAPIManager.endpointMapping]
      UAPIManager.apicodes = []
      
      UAPIManager.apiUpdateRequestActive = False
      
      UAPIManager.hit = App.webInterface.ConnectionManager.fetch
   
   def initialize ():
      UAPIManager.apiCall(
         apicode='api.getcodes',
         callback=UAPIManager.updateAPICode,
         quicksearch=False,
         apicoderequest=True,
         blocking=False,
         timeout=10000,
         caching=False,
      )
      UAPIManager.apiUpdateRequestActive = True
   
   def test ():
      print('api calling')
      print(
         'rrrr',
         UAPIManager.apiCall('api.test', blocking=True, timeout=4000,
         caching=False,),
      )
      print('api called')
      print(
         'rrrrr22222',
         UAPIManager.apiCall('api.test',
            callback=(lambda data: print('mdata', data)),
            blocking=False, timeout=100, caching=False,
         ),
      )
      print('api called2')
      print('xxx xapi callingx xxx')
      print(
         'aallll',
         UAPIManager.apiCall('api.test', blocking=True, timeout=6000,
         caching=False, data=UAPIManager.createData(
            kpo='koo', mno='tool', myspeech='I\'m kool',
         )),
      )
      print(
         'aklal',
         UAPIManager.apiCall('api.test', blocking=True, timeout=6000,
         caching=False, data='how am i?',)
      )
   
   def updateEndpoints (endpoints, connectionType=None):
      if ((not connectionType)
            or (connectionType not in UAPIManager.endpointMapping.keys())
         ):
         connectionType = App.webInterface.ConnectionManager.connectionType
      
      if (type(endpoints).__name__ not in ('tuple', 'list',)):
         oEndpoints = endpoints
         endpoints = [
            None for _ in UAPIManager.endpointMapping.keys()
         ]
         endpoints[UAPIManager.endpointMapping[connectionType]] = oEndpoints
      
      for eMapValue in UAPIManager.endpointMapping.values():
         UAPIManager.endpoints[eMapValue] = endpoints[eMapValue] or (
            UAPIManager.endpoints[eMapValue] or None
         )
   
   def getEndpoint (connectionType=None):
      if ((not connectionType)
            or (connectionType not in UAPIManager.endpointMapping.keys())
         ):
         connectionType = App.webInterface.ConnectionManager.connectionType
      
      return UAPIManager.endpoints[UAPIManager.endpointMapping[connectionType]]
   
   def updateAPICode (data):
      UAPIManager.apiUpdateRequestActive = False
      
      if (data.get('status') == App.Configuration.STATUS_SUCCESS):
         if (data.get('data')):
            apicodes = UAPIManager.apicodes.copy()
            apicodes.extend(data.get('data').get('apicodes') or [])
            
            UAPIManager.apicodes = list(set(apicodes))
   
   def createData (**kwargs):
      return (dict(kwargs))
   
   def apiCall (apicode, data=None, callback=None, quicksearch=False,
         apicoderequest=False, **kwargs,
      ):
      if (not data):
         data = {'apicode': apicode,}
      else:
         if (type(data).__name__ == 'dict'):
            data = {'apicode': apicode, 'data': data,}
         else:
            data = {'apicode': apicode, 'data': UAPIManager.createData(
                  value=data,
               ),
            }
      
      if ((apicode not in UAPIManager.apicodes) and (not apicoderequest)):
         if (not UAPIManager.apiUpdateRequestActive):
            UAPIManager.apiCall(
               apicode='api.getcodes',
               callback=UAPIManager.updateAPICode,
               quicksearch=False,
               apicoderequest=True,
               blocking=False,
               timeout=10000,
               caching=False,
            )
      
      if ((callback) and (not callable(callback))):
         return None
      
      if (quicksearch and (apicode not in UAPIManager.apicodes)):
         if (callback):
            callback(App.Configuration.apiErrorData.copy())
            return None
         else:
            return App.Configuration.apiErrorData.copy()
      elif (quicksearch and (apicode in UAPIManager.apicodes)):
         return UAPIManager.hit(data=data, callback=callback, **kwargs)
      else:
         return UAPIManager.hit(data=data, callback=callback, **kwargs)
