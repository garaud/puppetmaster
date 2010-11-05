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
import optparse

from puppetmaster import host


###################
# OPTIONS PARSING #
###################

# Parser instance.
usage = "%prog [options]"
parser = optparse.OptionParser(usage = usage)
parser.add_option("-f", "--file",
                  help="The name of the file where there are the host names."\
                      + " If it is not given, just tests the local host.",
                  metavar="FILE")
parser.add_option("--force-ssh-config", dest="forced_ssh", action="store_true",
                  default=False,
                  help="Uses the SSH configuration from PuppetMaster.")

(options, args) = parser.parse_args()

# If the number of arguments is wrong.
if len(args) >= 1:
    print "Improper usage!"
    print "Use option -h or --help for information about usage."
    sys.exit(1)

# A file is required.
if options.file is None:
    parser.error('A file is required. Please, use the option -f --file.'
                 + '\n-h --help for help.')


###############
# DECLARATION #
###############

# Host file name checking.
if not os.path.isfile(options.file):
    raise Exception, "The file '%s' not found." % options.file


##############
# PROCESSING #
##############

# Reads the host names.
f = open(options.file, 'r')
output = f.readlines()
f.close()

# Loop to declare and check each host.
for name in output:
    name = name.strip('\n')
    if len(name) != 0:
        host_instance = host.Host(name, options.forced_ssh)
        if host_instance.connection:
            print("%s -- OK" % name)
        else:
            print("%s -- off" % name)
