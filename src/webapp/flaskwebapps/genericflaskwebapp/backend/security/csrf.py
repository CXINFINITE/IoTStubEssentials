import re

from flask import (
   request,
   session,
   render_template,
)

import genericflaskwebapp as app

class CSRF:
   tokens = list()
   
   def get_csrf_token ():
      token = None
      
      while ((token in CSRF.tokens) or (not token)):
         token = app.backend.security.basickeygen.key_general_generate(
            length=64,
         )
      
      CSRF.tokens.append(token)
      
      return token
   
   def del_csrf_token (token):
      if (token in CSRF.tokens):
         CSRF.tokens.remove(token)
      
      return True
   
   def craft_token ():
      csrftoken = session.get('csrf_token')
      
      if ((not csrftoken) or (csrftoken and (csrftoken not in CSRF.tokens))):
         csrftoken = CSRF.get_csrf_token()
         
         session['csrf_token'] = csrftoken
      
      csrf_token = (
         '<input type="hidden" name="csrf_token" value="{0}" />'
      ).format(csrftoken)
      
      return csrf_token
   
   def verify_token (csrftoken):
      if ((not csrftoken)
         or (csrftoken
            and ((csrftoken != session.get('csrf_token'))
               or (csrftoken not in CSRF.tokens)
            )
         )
      ):
         return False
      
      return True
   
   def embedd_token (response):
      if (type(response).__name__ != 'str'):
         return response
      
      csrf_token = CSRF.craft_token()
      
      response = re.sub(
         (
            '([{][ ]*[cC][sS][rR][fF]'
            + '[_][tT][oO][kK][eE][nN][ ]*[}])'
         ),
         csrf_token,
         response,
         flags=re.DOTALL,
      )
      
      return response
   
   def render_template (*args, **kwargs):
      return CSRF.embedd_token(render_template(*args, **kwargs))
   
   def check_csrf_token (form=None):
      if (not form):
         form = request.form
      
      csrftoken = form.get('csrf_token')
      
      return (CSRF.verify_token(csrftoken))
