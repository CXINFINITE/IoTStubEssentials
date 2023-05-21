from flask import (
   request,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect()
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('home'),
)
@app.backend.decorators.authentication.get_logged_in_user()
def addtodo (user=None):
   note = request.form.get('note')
   
   registered = app.backend.functionality.ToDo.create(
      username=user.username,
      note=note,
   )
   
   if (not registered[0]):
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('dashboard'),
         error=registered[1],
      )
   
   return app.backend.core.redirect_internal.redirect(
      app.backend.router.routes.endpoints.get('dashboard'),
      success='ToDo note ({0}) created successfully'.format(
         registered[1].todoid,
      ),
   )
