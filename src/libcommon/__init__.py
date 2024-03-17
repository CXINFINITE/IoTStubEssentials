"""Library - collection of utilities.

This package contains utilities (or common programs) and are usually
independent. Though other programs may depend on these.
"""

from .identifier import Identifier as identifier
from .descriptoroperations import DescriptorOperations as descriptoroperations

__all__ = [
   'identifier',
   'descriptoroperations',
]
