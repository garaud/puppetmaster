# Copyright (C) 2009 INRIA - EDF R&D
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

import os, sys, commands
sys.path.insert(0, '../')
import network
sys.path.pop(0)


# HOME and DSH directories.
home_dir = os.environ['HOME']
dsh_dir = os.path.join(home_dir, '.dsh/group/')


# Exceptions.
if not os.path.isdir(dsh_dir):
    raise Exception, "The directory \"" + dsh_dir  + "\" does not exist." \
        + " Please install 'dsh' and create this directory."

if not os.path.isfile(os.path.join(dsh_dir, 'all')):
    raise Exception, "Please create the file 'all' in " \
        + dsh_dir + " with the name of all hosts."


# File where there are the list of hosts.
host_file = open(os.path.join(dsh_dir, 'all'), 'r')
host_list = host_file.readlines()
host_file.close()


# A loop to check the 'uptime' unix command for every hosts.
for host in host_list:
    command = 'ssh ' + host.strip() + ' uptime'
    (s, o) = commands.getstatusoutput(command)
    if s != 0:
        print "The command '" + command + "' failed."
