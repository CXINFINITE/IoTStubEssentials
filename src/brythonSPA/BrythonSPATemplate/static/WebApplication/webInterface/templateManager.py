import WebApplication as App

class TemplateManager:
   templates = {}
   
   def getTemplate (template, defaultValue=None):
      templateString = TemplateManager.templates.get(
         template,
         None,
      )
      
      if (templateString != None):
         return templateString
      
      try:
         with open(
               '{0}Templates/{1}.html'.format(
                  App.Configuration.staticUrl,
                  template,
               )
            ) as fh:
            templateString = fh.read() or ''
         
         if (len(templateString) > 1):
            TemplateManager.templates[template] = str(
               templateString
            )
         else:
            templateString = defaultValue
      except:
         templateString = defaultValue
      
      return templateString
   
   def render (template, **kwargs):
      return template.format(**kwargs)
