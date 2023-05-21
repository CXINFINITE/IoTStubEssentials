from flask import (
   redirect,
)

import genericflaskwebapp as app

@app.backend.decorators.authentication.login_required(
   app.backend.router.routes.endpoints.get('home'),
   internalredirect=True,
   success='Already logged out',
)
def logout ():
   app.backend.functionality.Authentication.logout()
   
   return redirect(app.backend.router.routes.endpoints.get('home'))
