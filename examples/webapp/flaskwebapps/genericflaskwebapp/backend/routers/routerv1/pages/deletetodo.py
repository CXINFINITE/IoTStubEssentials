from flask import (
   request,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect()
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('home'),
)
@app.backend.decorators.authentication.get_logged_in_user()
def deletetodo (user=None):
   todoid = request.form.get('todoid')
   
   deleted = app.backend.functionality.ToDo.delete(
      todoid=todoid,
   )
   
   if (not deleted[0]):
      return app.backend.core.redirect_internal.redirect(
         app.backend.router.routes.endpoints.get('dashboard'),
         error=deleted[1],
      )
   
   return app.backend.core.redirect_internal.redirect(
      app.backend.router.routes.endpoints.get('dashboard'),
      success='ToDo note ({0}) deleted successfully'.format(
         todoid,
      ),
   )
