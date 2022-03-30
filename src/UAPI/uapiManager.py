import re

class UAPIManager:
   APICodePattern = (
      '^[a-z]{1}[a-zA-Z0-9]*[a-z]{1}([\.]{1}[a-z]{1}[a-zA-Z0-9]*[a-z]{1})*$'
   )
   maxArgs = 20
   
   apis = dict()
   
   class Status:
      SUCCESS = 'success'
      FAILURE = 'failure'
      ERROR = 'error'
      
      class Reason:
         APICODE_REQUIRED = 'apicode required'
         INVALID_PARAMETERS = 'invalid parameters'
         
         UNDEFINED = 'unknown error occurred'
         API_UNDEFINED = 'invalid apicode'
         INTERNAL_ERROR = 'internal api error'
         
         # define your reasons here ...
         MY_REASON = 'my reason'
   
   def registerAPI (apicode, api_function=None, args=None, update=False):
      if ((type(apicode).__name__ != 'str')
            or ((not update) and (not api_function))
            or (update and (args == None) and (not api_function))
            or (api_function and (not callable(api_function)))
         ):
         return None
      
      if ((not update) and (args == None)):
         args = 0
      
      # Please bear with these if-elif-else statements.
      # I know these are in-efficient, but for quick rollout of this app,
      # I couldn't find time to change these up.
      
      if ((not update)
            and ((type(args).__name__ != 'int')
               or (args < 0) or (args > UAPIManager.maxArgs)
            )
         ):
         return None
      elif (update
            and (args)
            and ((type(args).__name__ != 'int')
               or (args < 0) or (args > UAPIManager.maxArgs)
            )
         ):
         return None
      elif (update
            and (args == None)
            and api_function
         ):
         pass
      elif (update
            and (args or (args == 0))
            and (not api_function)
         ):
         pass
      elif (update
            and (args or (args == 0))
            and api_function
         ):
         pass
      elif ((not update)
            and (args or (args == 0))
            and api_function
         ):
         pass
      else:
         return None
      
      if (not bool(re.fullmatch(UAPIManager.APICodePattern, apicode,))):
         return None
      
      apistatus = UAPIManager.getAvailableAPIs(apicode)
      
      if ((not apistatus)
            and ((not api_function)
               or (api_function and (not callable(api_function)))
            )
         ):
         return False
      
      if (apistatus and (not update)):
         return False
      elif (not apistatus):
         args = args or 0
         UAPIManager.apis[apicode] = [api_function, args]
         return True
      elif (apistatus and update):
         if (api_function and callable(api_function)):
            UAPIManager.apis[apicode][0] = api_function
         
         if (args or (args == 0)):
            UAPIManager.apis[apicode][1] = args
         
         return True
      else:
         return False
   
   def unregisterAPI (apicode):
      if (type(apicode).__name__ != 'str'):
         return None
      
      apistatus = UAPIManager.getAvailableAPIs(apicode)
      
      if (not apistatus):
         return False
      elif (apistatus):
         UAPIManager.apis.pop(apicode)
         return True
      else:
         return False
   
   def getAvailableAPIs (apicode=None):
      if (apicode and (type(apicode).__name__ == 'str')):
         return (apicode in UAPIManager.apis.keys())
      elif (apicode):
         return None
      else:
         return tuple(set(UAPIManager.apis.keys()))
   
   def getAPI (apicode, getargs=False):
      if (apicode
            and (type(apicode).__name__ == 'str')
            and (UAPIManager.getAvailableAPIs(apicode))
         ):
         if (getargs):
            return (UAPIManager.apis.get(apicode)[1] or 0)
         else:
            return (UAPIManager.apis.get(apicode)[0])
      else:
         return None
   
   def createResponse (status=None, data=None, reason=None,
         maxParameters=None, **kwargs,
      ):
      if (not status):
         if (data):
            status = UAPIManager.Status.SUCCESS
         else:
            status = UAPIManager.Status.FAILURE
            if (not reason):
               reason = UAPIManager.Status.Reason.INTERNAL_ERROR
      elif (status):
         if (type(status).__name__ != 'str'):
            status = UAPIManager.Status.SUCCESS
         else:
            if ((status == UAPIManager.Status.ERROR) and (not reason)):
               reason = UAPIManager.Status.Reason.UNDEFINED
      
      if (not data):
         data = dict(kwargs)
      elif (data):
         if (type(data).__name__ != 'dict'):
            odata = data
            data = dict(kwargs)
            data['responseValue'] = odata
         elif (type(data).__name__ == 'dict'):
            data.update(dict(kwargs))
      
      data = data or None
      
      response = {
         'status': status,
      }
      
      if (reason and (type(reason).__name__ == 'str')):
         response['reason'] = reason
      
      if (maxParameters and (type(maxParameters).__name__ == 'int')):
         response['maxParameters'] = maxParameters
      
      if (data):
         response['data'] = data
      
      return response
   
   def fetch (request=None, apicode=None, data=None, path=[],):
      path = path or []
      
      if (apicode):
         if (UAPIManager.getAvailableAPIs(apicode)):
            args = UAPIManager.getAPI(apicode, getargs=True)
            
            if (len(path) > args):
               response = UAPIManager.createResponse(
                  status=UAPIManager.Status.ERROR,
                  reason=UAPIManager.Status.Reason.INVALID_PARAMETERS,
                  maxParameters=args,
               )
            elif (len(path) <= args):
               path = path[:args]
               
               try:
                  response = UAPIManager.getAPI(
                     apicode, getargs=False,
                  )(request, data, *path,)
               except:
                  response = UAPIManager.createResponse(
                     status=UAPIManager.Status.ERROR,
                     reason=UAPIManager.Status.Reason.INTERNAL_ERROR,
                  )
               
               if (not response):
                  response = UAPIManager.createResponse(
                     status=False,
                     reason=UAPIManager.Status.Reason.UNDEFINED,
                  )
            else:
               response = UAPIManager.createResponse(
                  status=UAPIManager.Status.ERROR,
                  reason=UAPIManager.Status.Reason.UNDEFINED,
               )
         else:
            response = UAPIManager.createResponse(
               status=UAPIManager.Status.ERROR,
               reason=UAPIManager.Status.Reason.API_UNDEFINED,
            )
      else:
         response = UAPIManager.createResponse(
            status=UAPIManager.Status.ERROR,
            reason=UAPIManager.Status.Reason.APICODE_REQUIRED,
         )
         
      return response
