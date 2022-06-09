import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).resolve().parent.parent
))

import BrythonModulesUpdater as App

if __name__ == '__main__':
   App.core.Executor.execute_from_cli()
   exit(0)
