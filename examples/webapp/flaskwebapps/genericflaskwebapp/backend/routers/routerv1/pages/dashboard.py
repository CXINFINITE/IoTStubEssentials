from flask import (
   render_template,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect(
   check=False,
)
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('home'),
)
@app.backend.decorators.authentication.get_logged_in_user()
@app.backend.decorators.redirect_internal.check(
   app.backend.router.routes.endpoints.get('dashboard'),
)
def dashboard (redirectiondata={}, user=None):
   todos = (app.database.models.ToDo.get_todos(
      username=user.username,
   ) or [])
   
   return render_template(
      'dashboard.html',
      success=redirectiondata.get('success'),
      error=redirectiondata.get('error'),
      user=user, todos=todos,
      logouturl=app.backend.router.routes.endpoints.get('logout'),
      addtodourl=app.backend.router.routes.endpoints.get('addtodo'),
      deletetodourl=app.backend.router.routes.endpoints.get('deletetodo'),
      deleteuserurl=app.backend.router.routes.endpoints.get('deleteuser'),
   )
