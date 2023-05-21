import genericflaskwebapp as app

class Routes:
   endpoints = {
      'home' : '/',
      
      'signup': '/signup',
      'login' : '/login',
      
      'logout' : '/logout',
      
      'dashboard': '/dashboard',
      
      'addtodo' : '/addtodo',
      'deletetodo': '/deletetodo',
      'deleteuser': '/deleteuser',
   }
   
   def route_webapp (webapp):
      from . import pages
      
      @webapp.route(Routes.endpoints.get('home'))
      def home (*args, **kwargs):
         return pages.home(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('signup'), methods=['POST'])
      def signup (*args, **kwargs):
         return pages.signup(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('deleteuser'), methods=['POST'])
      def deleteuser (*args, **kwargs):
         return pages.deleteuser(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('login'), methods=['POST'])
      def login (*args, **kwargs):
         return pages.login(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('logout'), methods=['GET', 'POST'])
      def logout (*args, **kwargs):
         return pages.logout(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('addtodo'), methods=['POST'])
      def addtodo (*args, **kwargs):
         return pages.addtodo(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('deletetodo'), methods=['POST'])
      def deletetodo (*args, **kwargs):
         return pages.deletetodo(*args, **kwargs)
      
      @webapp.route(Routes.endpoints.get('dashboard'))
      def dashboard (*args, **kwargs):
         return pages.dashboard(*args, **kwargs)
      
      return True
