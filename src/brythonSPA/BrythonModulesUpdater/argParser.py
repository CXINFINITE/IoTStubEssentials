import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import argparse
import BrythonModulesUpdater as App

class ArgParser:
   def start ():
      ArgParser.parser = argparse.ArgumentParser(
         description=(
            'A program to update / generate brython modules for '
            + 'brython single page web application (SPA).'
         ),
         epilog=(
            'Designed and developed for rapid brython single page web '
            + 'application (SPA) development.'
         ),
      )
      
      ArgParser.parser.add_argument(
         'applicationName',
         action='store',
         type=str,
         metavar='application-name',
         help=(
            'Name of application to update under brython SPA webPages.\n'
            + '<base-path>/<base-application-name>/<web-pages-dir-name>/ '
            + 'should have <application-name>.__init__.py file '
            + 'and <application-name> directory.'
         ),
      )
      ArgParser.parser.add_argument(
         'subApplicationName',
         action='store',
         type=str,
         nargs='?',
         metavar='sub-application-name',
         default=None,
         help=(
            'Name of subapplication (inside application, if any) '
            + 'to update under brython SPA webPages.\n'
            + '<base-path>/<base-application-name>/<web-pages-dir-name>/'
            + '<application-name>/ directory should have '
            + '<sub-application-name> directory and '
            + '<sub-application-name>.__init__.py file.'
         ),
      )
      
      ArgParser.parser.add_argument(
         '-bP', '--base-path',
         action='store',
         type=Path,
         required=False,
         metavar='base-path',
         dest='basePath',
         nargs=1,
         default=App.Configuration.basePath,
         help=(
            'Path to base directory of brython SPA.\n'
            + 'This directory must contain <base-application-name> directory '
            + 'and <base-application-name>.py file.'
         ),
      )
      ArgParser.parser.add_argument(
         '-bN', '--base-name', '--base-application-name',
         action='store',
         type=str,
         required=False,
         metavar='base-application-name',
         dest='baseApplicationName',
         nargs=1,
         default=App.Configuration.baseApplicationName,
         help=(
            'Name of base brython SPA (outermost .py file and directory).\n'
            + 'Base path must contain <base-application-name>.py file as well '
            + 'as <base-application-name> directory.'
         ),
      )
      
      ArgParser.parser.add_argument(
         '-o', '-oP', '--output', '--output-path', '--output-dir-path',
         action='store',
         type=Path,
         required=False,
         metavar='output-dir-path',
         dest='jsDirPath',
         nargs=1,
         default=None,
         help=(
            'Path to output directory.\n'
            + 'brython_modules.js file will be (over) written to this '
            + 'directory.'
         ),
      )
      
      ArgParser.parser.add_argument(
         '-aF', '--app-files',
         action='extend',
         type=str,
         required=False,
         metavar='filename',
         dest='requiredAppFiles',
         nargs='+',
         help=(
            'Names of files required in base brython SPA.\n'
            + 'List of files (not directories) to include from '
            + '<base-path>/<base-application-name>/ to generate module file.'
         ),
      )
      ArgParser.parser.add_argument(
         '-aD', '--app-dirs',
         action='extend',
         type=str,
         required=False,
         metavar='directoryname',
         dest='requiredAppDirs',
         nargs='+',
         help=(
            'Names of directories required in base brython SPA.\n'
            + 'List of directories to include from '
            + '<base-path>/<base-application-name>/ to generate module file.'
         ),
      )
      ArgParser.parser.add_argument(
         '-wN', '--web-pages-name', '--web-pages-dir-name',
         action='store',
         type=str,
         required=False,
         metavar='directoryname',
         dest='webPagesDirName',
         nargs=1,
         default=App.Configuration.webPagesDirName,
         help=(
            'Name of webPages directory containing applications '
            + 'in base brython SPA.\n'
            + 'Name of directory inside <base-path>/<base-application-name>/'
            + 'which contains <application-name> and / or '
            + '<application-name>/<sub-application-name> directory(ies) '
            + '(if exists).'
         ),
      )
      ArgParser.parser.add_argument(
         '-wF', '--web-pages-files',
         action='extend',
         type=str,
         required=False,
         metavar='filename',
         dest='requiredWebPagesFiles',
         nargs='+',
         help=(
            'Names of files required in webPages directory '
            + 'in base brython SPA.\n'
            + 'List of files (not directories) to include from '
            + '<base-path>/<base-application-name>/<web-pages-dir-name>/ '
            + 'to generate module file.'
         ),
      )
      ArgParser.parser.add_argument(
         '-wD', '--web-pages-dirs',
         action='extend',
         type=str,
         required=False,
         metavar='directoryname',
         dest='requiredWebPagesDirs',
         nargs='+',
         help=(
            'Names of directories required in webPages directory '
            + 'in base brython SPA.\n'
            + 'List of directories to include from '
            + '<base-path>/<base-application-name>/<web-pages-dir-name>/ '
            + 'to generate module file.'
         ),
      )
      
      ArgParser.parser.add_argument(
         '-i', '--intermediate', '--intermediate-files',
         action='store_true',
         required=False,
         dest='intermediateFiles',
         help=(
            'Use this flag to generate intermediate files and directories '
            + 'used to generate final output / module file.'
         ),
      )
      ArgParser.parser.add_argument(
         '-c', '--command', '--brython-command', '--brython-cli-command',
         action='store',
         type=str,
         required=False,
         metavar="'system-command'",
         dest='brythonCliModulesCommand',
         nargs=1,
         default=App.Configuration.brythonCliModulesCommand,
         help=(
            'System command to generate brython modules (file) from cli.'
         ),
      )
      
      ArgParser.parser.add_argument(
         '-v', '--verbose',
         action='count',
         default=0,
      )
      
      ArgParser.parser.add_argument(
         '-V', '--version',
         action='version',
         version=('{0} v{1}'.format(
               App.Configuration.appName,
               App.Configuration.version,
            )
         ),
      )
   
   def parse_args (*args, **kwargs):
      if (not ArgParser.parser): return None
      
      return ArgParser.parser.parse_args(*args, **kwargs)
