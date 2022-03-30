from django.urls import (include, path,)

urlpatterns = [
   path('uapi/', include('uapi.urls', namespace='uapi')),
   path('', include('webapplication.urls', namespace='webapplication')),
   # other urls ...
]

# other setup, if any ...
