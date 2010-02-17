# __init__.py
# Copyright (C) 2010 INRIA - EDF R&D
# Authors: Damien Garaud
#
# This file is part of the PuppetMaster project. It provides facilities to
# deal with computations over a Linux network.
#
# This script is free; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.

"""
\namespace puppetmaster
\package src

Imports all PuppetMaster modules.

\author Damien Garaud
"""

import os
import inspect

from host import Host
from network import Network
from program_manager import Configuration, Program, ProgramManager


__all__ = [ name for name, obj in locals().items()
            if not (name.startswith('_') or inspect.ismodule(obj)) ]
