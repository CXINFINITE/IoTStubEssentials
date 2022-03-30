import WebApplication as App

class APIManager:
   endpoints = None
   endpointMapping = None
   apicodes = None
   
   apiUpdateRequestActive = None
   
   def start ():
      APIManager.endpointMapping = {
         'ajax': -1,
         'websocket': 0,
      }
      APIManager.endpoints = [None for _ in APIManager.endpointMapping]
      APIManager.apicodes = []
      
      APIManager.apiUpdateRequestActive = False
      
      APIManager.hit = App.webInterface.ConnectionManager.fetch
   
   def initialize ():
      APIManager.apiCall(
         apicode='api.getcodes',
         callback=APIManager.updateAPICode,
         quicksearch=False,
         apicoderequest=True,
         blocking=False,
         timeout=10000,
         caching=False,
      )
      APIManager.apiUpdateRequestActive = True
   
   def test ():
      print('api calling')
      print(
         'rrrr',
         APIManager.apiCall('api.test', blocking=True, timeout=4000,
         caching=False,),
      )
      print('api called')
      print(
         'rrrrr22222',
         APIManager.apiCall('api.test',
            callback=(lambda data: print('mdata', data)),
            blocking=False, timeout=100, caching=False,
         ),
      )
      print('api called2')
      print('xxx xapi callingx xxx')
      print(
         'aallll',
         APIManager.apiCall('api.test', blocking=True, timeout=6000,
         caching=False, data=APIManager.createData(
            kpo='koo', mno='tool', myspeech='I\'m kool',
         )),
      )
      print(
         'aklal',
         APIManager.apiCall('api.test', blocking=True, timeout=6000,
         caching=False, data='how am i?',)
      )
   
   def updateEndpoints (endpoints, connectionType=None):
      if ((not connectionType)
            or (connectionType not in APIManager.endpointMapping.keys())
         ):
         connectionType = App.webInterface.ConnectionManager.connectionType
      
      if (type(endpoints).__name__ not in ('tuple', 'list',)):
         oEndpoints = endpoints
         endpoints = [
            None for _ in APIManager.endpointMapping.keys()
         ]
         endpoints[APIManager.endpointMapping[connectionType]] = oEndpoints
      
      for eMapValue in APIManager.endpointMapping.values():
         APIManager.endpoints[eMapValue] = endpoints[eMapValue] or (
            APIManager.endpoints[eMapValue] or None
         )
   
   def getEndpoint (connectionType=None):
      if ((not connectionType)
            or (connectionType not in APIManager.endpointMapping.keys())
         ):
         connectionType = App.webInterface.ConnectionManager.connectionType
      
      return APIManager.endpoints[APIManager.endpointMapping[connectionType]]
   
   def updateAPICode (data):
      APIManager.apiUpdateRequestActive = False
      
      if (data.get('status') == 'success'):
         if (data.get('data')):
            apicodes = APIManager.apicodes.copy()
            apicodes.extend(data.get('data').get('apicodes') or [])
            
            APIManager.apicodes = list(set(apicodes))
   
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
            data = {'apicode': apicode, 'data': APIManager.createData(
                  value=data,
               ),
            }
      
      if ((apicode not in APIManager.apicodes) and (not apicoderequest)):
         if (not APIManager.apiUpdateRequestActive):
            APIManager.apiCall(
               apicode='api.getcodes',
               callback=APIManager.updateAPICode,
               quicksearch=False,
               apicoderequest=True,
               blocking=False,
               timeout=10000,
               caching=False,
            )
      
      if ((callback) and (not callable(callback))):
         return None
      
      if (quicksearch and (apicode not in APIManager.apicodes)):
         if (callback):
            callback(App.Configuration.apiErrorData.copy())
            return None
         else:
            return App.Configuration.apiErrorData.copy()
      elif (quicksearch and (apicode in APIManager.apicodes)):
         return APIManager.hit(data=data, callback=callback, **kwargs)
      else:
         return APIManager.hit(data=data, callback=callback, **kwargs)
