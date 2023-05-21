from flask import (
   request,
   redirect,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect()
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('dashboard'),
   invert=True,
)
def login ():
   username = request.form.get('username')
   password = request.form.get('password')
   
   loggedin = app.backend.functionality.Authentication.login(
      username=username,
      password=password,
   )
   
   if (not loggedin[0]):
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('home'),
         error=loggedin[1],
      )
   
   return redirect(app.backend.router.routes.endpoints.get('dashboard'))
