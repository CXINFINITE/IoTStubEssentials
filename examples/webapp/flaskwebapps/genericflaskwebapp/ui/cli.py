import os
import argparse
import genericflaskwebapp as app

operationmodes_aliases = {
   'webserver': [
      'ws',
      'web',
      'server',
      'webs',
      'wserver',
   ],
}

databases = [
   'sqlite3',
]

models = [
   'modelsv1',
]

routers = [
   'routerv1',
]

def argparser_get ():
   parser = argparse.ArgumentParser(
      description=(
         '{0}:\n'.format(
            app.__version__.appname,
         )
         + 'Simple, python-flask based generic web app demo.'
      ),
      epilog=(
         'Designed and developed by {0} ! [Github: {1}]'.format(
            app.__author__.name,
            app.__author__.github,
         )
      ),
   )
   
   subparsers = parser.add_subparsers(
      title='Modes',
      description='{0} operation mode(s).'.format(app.__version__.fullappname),
      required=True,
      dest='mode',
      help='Select an operation mode.',
   )
   
   parser_webserver= subparsers.add_parser(
      'webserver',
      aliases=operationmodes_aliases.get('webserver', []),
   )
   parser_webserver.add_argument(
      '-i', '--ip', '--host', '--ip-address',
      action='store',
      type=str,
      required=False,
      metavar='host',
      dest='host',
      nargs='?',
      default=None,
      help=(
         'IP / host address for flask '
         + '(default = 0.0.0.0).'
      ),
   )
   parser_webserver.add_argument(
      '-p', '--port',
      action='store',
      type=int,
      required=False,
      metavar='port',
      dest='port',
      nargs='?',
      default=None,
      help=(
         'Port number for flask '
         + '(default = 5000). '
      ),
   )
   parser_webserver.add_argument(
      '-dB', '--database',
      action='store',
      type=str,
      required=False,
      metavar='database',
      dest='database',
      nargs='?',
      default=None,
      help=(
         'Database to use'
         + '(default = \'SQLite3\').'
      ),
   )
   parser_webserver.add_argument(
      '-dP', '--db-path', '--database-path',
      action='store',
      type=str,
      required=False,
      metavar='databasepath',
      dest='databasepath',
      nargs='?',
      default=None,
      help=(
         'Path to database '
         + '(default = \'storage/databases/database.sqlite3\').'
      ),
   )
   parser_webserver.add_argument(
      '-tP', '--templates-path',
      action='store',
      type=str,
      required=False,
      metavar='templatespath',
      dest='templatespath',
      nargs='?',
      default=None,
      help=(
         'Path to templates '
         + '(default = \'frontend/templates/\').'
      ),
   )
   parser_webserver.add_argument(
      '-m', '--model',
      action='store',
      type=str,
      required=False,
      metavar='model',
      dest='model',
      nargs='?',
      default=None,
      help=(
         'Models to use '
         + '(default = \'ModelsV1\').'
      ),
   )
   parser_webserver.add_argument(
      '-r', '--router',
      action='store',
      type=str,
      required=False,
      metavar='router',
      dest='router',
      nargs='?',
      default=None,
      help=(
         'Router to use '
         + '(default = \'RouterV1\').'
      ),
   )
   parser_webserver.add_argument(
      '-v', '--verbose',
      action='count',
      dest='verbosity',
      default=0,
      help='Increase output verbosity.',
   )
   parser_webserver.add_argument(
      '-D', '--no-debug',
      action='store_false',
      required=False,
      dest='debug',
      default=None,
      help=(
         'Set debug mode to False (default = True).'
      ),
   )
   
   parser.add_argument(
      '-V', '--version',
      action='version',
      version=('{0}'.format(
            app.__version__.description,
         )
      ),
   )
   parser.add_argument(
      '-v', '--verbose',
      action='count',
      dest='verbosity',
      default=0,
      help='increase output verbosity',
   )
   
   return parser

def argparser_parse_args (*args, **kwargs):
   parser = argparser_get()
   parsed = parser.parse_args(*args, **kwargs)
   
   return (parser, parsed)

def execute ():
   parser, parsed_args = argparser_parse_args()
   
   if (not parsed_args):
      raise Exception('ui.cli.execute: cli not parsed')
   
   if (parsed_args.mode not in operationmodes_aliases):
      for mode, aliases in operationmodes_aliases.items():
         if (parsed_args.mode in aliases):
            parsed_args.mode = mode
            break
   
   if (parsed_args.mode not in operationmodes_aliases):
      parser.error('Invalid operation mode')
   
   if (parsed_args.mode == 'webserver'):
      if (parsed_args.database):
         if (parsed_args.database.lower() not in databases):
            parser.error('Invalid database')
         
         parsed_args.database = (
            databases.index(parsed_args.database.lower()) + 1
         )
      
      if (parsed_args.model):
         if (parsed_args.model.lower() not in models):
            parser.error('Invalid model')
         
         parsed_args.model = (
            models.index(parsed_args.model.lower()) + 1
         )
      
      if (parsed_args.router):
         if (parsed_args.router.lower() not in routers):
            parser.error('Invalid router')
         
         parsed_args.router = (
            routers.index(parsed_args.router.lower()) + 1
         )
      
      if (parsed_args.databasepath):
         parsed_args.databasepath = os.path.abspath(parsed_args.databasepath)
      
      if (parsed_args.templatespath):
         parsed_args.templatespath = os.path.abspath(parsed_args.templatespath)
   
   return parsed_args
