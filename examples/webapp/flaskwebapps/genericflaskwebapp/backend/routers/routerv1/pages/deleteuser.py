from flask import (
   request,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect()
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('home'),
)
@app.backend.decorators.authentication.get_logged_in_user()
def deleteuser (user=None):
   username = request.form.get('username')
   
   if ((not username) or (username != user.username)):
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('dashboard'),
         error='Invalid user deletion request',
      )
   
   app.backend.functionality.ToDo.delete(
      username=user.username,
   )
   
   try:
      user.delete()
   except:
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('dashboard'),
         error='User account ({0}) deletion failure'.format(
            user.username,
         ),
      )
   
   app.backend.functionality.Authentication.logout()
   
   return app.backend.core.redirect_internal.redirect(
      app.backend.router.routes.endpoints.get('home'),
      success='User account ({0}) deleted successfully'.format(
         username,
      ),
   )
