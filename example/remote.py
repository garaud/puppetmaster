# Copyright (C) 2009-2010 INRIA
# Authors: Damien Garaud
#
#  This file is part of the PuppetMaster project. It is an example for the
#  module 'network.py'.
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

import socket
import random

from puppetmaster import network


##################
# ACCESS METHODS #
##################

# A network.Network instance.
net = network.Network()

# Gets the name of hosts in a list.
host_list = net.GetHostNames()

# Gets the load averages (1 minute) for each host (a list of tuples).
load_avr_list = net.GetUptime()

# The minimal load average in the list.
min_load_avr = min([x[1] for x in load_avr_list])

# The list of available hosts with their number of free processors.
available_host_list = net.GetAvailableHosts()


######################
# PROCESSING METHODS #
######################

command_name = "echo 'Hello World!'"

# A random host.
index = random.randint(0, len(net.hosts) - 1)
random_host = net.hosts[index].name
while (random_host == socket.gethostname() and len(net.hosts) != 1):
    index = random.randint(0, len(net.hosts) - 1)
    random_host = net.hosts[index].name

# Launches an interactive command on a local host (without 2nd argument).
status = net.LaunchInt(command_name)
# 'status' must be equal to 0.
# Launches an interactive command on a remote host.
status = net.LaunchInt(command_name, random_host)

# Launches a foreground command.
(status, output) = net.LaunchFG(command_name)
# On a remote host.
(status, output) = net.LaunchFG(command_name, random_host)

# Launches a foreground command.
processus = net.LaunchBG(command_name)
# On a remote host.
processus = net.LaunchBG(command_name, random_host)
# processus.poll() = 0 or -1 if the processus is not finished.

# Launches a subprocess.
subproc = net.LaunchSubProcess(command_name, random_host)
# subproc.poll() must be equal to 0, None (if the process is not finished).
# subproc.communicate() to display the stdout and the stderr of the command.

# If you want to send a mail.
message = "This is just a test."
# net.SendMail(subject='[network.py]: Test',
#              fromaddr='graudd@cerea.enpc.fr',
#              toaddr='damien.garaud@inria.fr', msg=message)
