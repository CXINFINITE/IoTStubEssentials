import genericflaskwebapp as app

class API:
   class Router:
      RouterV1 = 1
   
   def router_start (router):
      if (router == API.Router.RouterV1):
         from .routers import routerv1
         
         app.backend.router = routerv1
      
      return True
