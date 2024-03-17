"""Library - collection of progress mechanisms.

This package contains progress mechanisms which can be used to synchronize
program operations and centrally control or monitor them as needed.
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(
   Path(__file__).parent.parent.resolve(),
))

from . import (
   trigger,
)

__all__ = [
   'trigger',
]
