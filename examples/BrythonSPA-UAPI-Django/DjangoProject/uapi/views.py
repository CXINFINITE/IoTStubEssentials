import re
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .uapiManager import UAPIManager

from .apis import APIs

APIs.start()

# Create your views here.

@csrf_exempt
def restapi (request, path=None,):
   apicode = None
   
   if (path):
      path = [
         (
            int(ipath)
            if (str(ipath).isdigit())
            else str(ipath)
         )
         for ipath in [
            re.sub('[\ ]+', ' ', apath.strip())
            for apath in re.split('[^a-zA-Z0-9\-\.\ ]+', path)
            if (apath)
         ]
         if (ipath)
      ]
      
      if (len(path) > 0):
         apicode = str(path[0]).strip().replace(' ', '') or None
         path = path[1:]
   else:
      path = []
   
   requestdata = None
   try:
      requestdata = json.loads(request.body)
   except:
      requestdata = None
   
   if (requestdata):
      if (not apicode):
         apicode = requestdata.get('apicode')
      
      requestdata = requestdata.get('data')
   else:
      requestdata = dict()
      for key, value in request.GET.items():
         requestdata[key] = value
      
      for key, value in request.POST.items():
         requestdata[key] = value
      
      if (not apicode):
         apicode = requestdata.get('apicode')
      
      try:
         requestdata.pop('apicode')
      except:
         pass
   
   if (apicode):
      apicode = apicode.replace('-', '.')
   
   requestdata = requestdata or dict()
   
   # modify data or request as required.
   
   data = UAPIManager.fetch(request,
      apicode=apicode, data=requestdata, path=path,
   )
   
   return HttpResponse (
      json.dumps(data),
      content_type='application/json',
   )

# your code ...
