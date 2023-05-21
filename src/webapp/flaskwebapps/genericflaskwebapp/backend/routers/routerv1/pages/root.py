from flask import (
   render_template,
)

import genericflaskwebapp as app

@app.backend.decorators.csrf.csrf_protect(
   check=False,
)
@app.backend.decorators.redirect_internal.check(
   app.backend.router.routes.endpoints.get('root'),
)
def root (redirectiondata={}):
   return render_template(
      'root.html',
   )
