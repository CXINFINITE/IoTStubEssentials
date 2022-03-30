from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index (request, application=None, tab=None, subtab=None):
   capp = str(application or 'Application2') # default
   
   # Check conditions to fill application name and subapplication name in
   # capp and csubapp
   
   capp = 'Application1'
   csubapp = 'SubApplication1'
   
   module = '{0}{1}'.format(
      capp,
      (''
         if (not csubapp)
         else (
            '.{0}'.format(csubapp)
         )
      ),
   )
   
   return render(
      request,
      'webapplication/WebApplication.index.html',
      {
         'module': module,
         'capp': capp,
         'csubapp': csubapp,
         'tabname': str(tab or '').lower(),
         'subtabname': str(subtab or '').lower(),
      },
   )
