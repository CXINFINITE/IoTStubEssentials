import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).parent.resolve(),
))
sys.path.append(os.path.abspath(
   Path(__file__).parent.parent.resolve(),
))

from ui_bridge import execute_cli

if __name__ == '__main__':
   execute_cli()
