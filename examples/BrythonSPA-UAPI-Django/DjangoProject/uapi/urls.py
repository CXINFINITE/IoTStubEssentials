from django.urls import path

from . import views

app_name = 'uapi'

urlpatterns = [
   path(
      'uapi/',
      views.uapi, name='uapi',
   ),
   path(
      'uapi/<path:path>/',
      views.uapi, name='uapi',
   ),
   # other views ...
]

# your code ...
