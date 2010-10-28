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

import os
import sys

from puppetmaster import host


#############
# ARGUMENTS #
#############

help_message = \
"""
Usage:
 python %s [host_file] [forced_ssh_config]
 Checks the connection to each host defined in a file.

Arguments:
 [host_file]: the file where the host names are defined (one for each line).
 [forced_ssh_config]: uses the SSH configuration from PuppetMaster (optional).
""" % sys.argv[0]

if len(sys.argv) == 2:
    host_file = sys.argv[1]
    forced_ssh = 'no'
elif len(sys.argv) == 3:
    host_file = sys.argv[1]
    forced_ssh = sys.argv[2]
else:
    print help_message
    sys.exit(0)

if forced_ssh not in ['no', 'yes']:
    print help_message
    print "Second argument [forced_ssh_config] must be 'yes' or 'no'."
    print "'no' by default."
    sys.exit(0)


###############
# DECLARATION #
###############

# Host file name checking.
if not os.path.isfile(host_file):
    raise Exception, "The file '%s' not found." % host_file

# Forces SSH configuration?
if forced_ssh == 'yes':
    forced_ssh = True
else:
    forced_ssh = False


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
    if len(name) != 0:
        host_instance = host.Host(name, forced_ssh)
        if host_instance.connection:
            print("%s -- OK" % name)
        else:
            print("%s -- off" % name)
