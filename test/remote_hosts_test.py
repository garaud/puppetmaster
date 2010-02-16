# Copyright (C) 2009-2010 INRIA - EDF R&D
# Author: Damien Garaud
#
# This file is part of the PuppetMaster project. It checks the access to
# remote hosts.
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

import os, sys
sys.path.insert(0, '../src')
import host
sys.path.pop(0)


#############
# ARGUMENTS #
#############

help_message = \
"""
Usage:
 python %s [host_file]
 Checks the connection to each host defined in a file.

Arguments:
 [host_file]: the file where the host names are defined (one for each line).
""" % sys.argv[0]

if len(sys.argv) != 2:
    print help_message
    sys.exit(0)
else:
    host_file = sys.argv[1]


###############
# DECLARATION #
###############

# Host file name checking.
if not os.path.isfile(host_file):
    raise Exception, "The file '%s' not found." % host_file


##############
# PROCESSING #
##############

# Reads the host names.
f = open(host_file, 'r')
output = f.readlines()
f.close()

# Loop to declare and check each host.
for name in output:
    name = name.strip('\n')
    host_instance = host.Host(name, forced_ssh_config = True)
    if host_instance.connection:
        print("%s -- OK" % name)
