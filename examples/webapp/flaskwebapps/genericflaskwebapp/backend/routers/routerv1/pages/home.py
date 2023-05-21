from flask import (
   render_template,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect(
   check=False,
)
@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('dashboard'),
   invert=True,
)
@app.backend.decorators.redirect_internal.check(
   app.backend.router.routes.endpoints.get('home'),
)
def home (redirectiondata={}):
   return render_template(
      'home.html',
      success=redirectiondata.get('success'),
      error=redirectiondata.get('error'),
      signupurl=app.backend.router.routes.endpoints.get('signup'),
      loginurl=app.backend.router.routes.endpoints.get('login'),
   )
