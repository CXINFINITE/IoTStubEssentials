from django.urls import path

from . import views

app_name = 'webapplication'

urlpatterns = [
   path('', views.index, name='index'),
   path('<slug:application>/', views.index, name='index'),
   path('<slug:application>/<slug:tab>/', views.index, name='index'),
   path(
      '<slug:application>/<slug:tab>/<slug:subtab>/',
      views.index,
      name='index',
   ),
   # other views ...
]

# your code ...
