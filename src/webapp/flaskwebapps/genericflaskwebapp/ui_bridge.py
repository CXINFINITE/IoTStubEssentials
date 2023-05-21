import sys
from ui import cli

def execute_cli ():
   parsed_args = cli.execute()
   
   if (parsed_args.mode == 'webserver'):
      from operations import webserver
      
      try:
         exechandler = webserver.Executor(
            host=parsed_args.host,
            port=parsed_args.port,
            database=parsed_args.database,
            dbpath=parsed_args.databasepath,
            templatespath=parsed_args.templatespath,
            model=parsed_args.model,
            router=parsed_args.router,
            debug=parsed_args.debug,
         )
         
         exechandler.start()
      except KeyboardInterrupt:
         print('Exiting ...')
      except:
         print('Unkown exception, Terminating !')
         raise
   else:
      raise Exception('ui_bridge.execute_cli: invalid operation mode')
   
   sys.exit(0)
   
   return None
