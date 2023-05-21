import genericflaskwebapp as app

class Routes:
   endpoints = {
      'root' : '/',
   }
   
   def route_webapp (webapp):
      from . import pages
      
      @webapp.route(Routes.endpoints.get('root'))
      def root (*args, **kwargs):
         return pages.root(*args, **kwargs)
      
      return True
