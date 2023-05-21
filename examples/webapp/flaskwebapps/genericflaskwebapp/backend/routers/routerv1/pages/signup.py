from flask import (
   request,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect()
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('dashboard'),
   invert=True,
)
def signup ():
   username = request.form.get('username')
   name = request.form.get('name')
   password = request.form.get('password')
   
   registered = app.backend.functionality.User.create(
      username=username,
      name=name,
      password=password,
   )
   
   if (not registered[0]):
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('home'),
         error=registered[1],
      )
   
   return app.backend.core.redirect_internal.redirect(
      app.backend.router.routes.endpoints.get('home'),
      success='User account registered successfully, try loggin in',
   )
