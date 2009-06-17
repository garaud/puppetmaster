# Copyright (C) 2009 INRIA
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

import sys, socket, random
sys.path.insert(0, '../')
import network
sys.path.pop(0)


##################
# ACCESS METHODS #
##################

# A network.Network instance.
net = network.Network()

# Gets the name of hosts in a list.
host_list = net.GetHostNames()

# Gets the load averages (1 minute) for each host (a list of tuples).
load_avr_list = net.GetLoadAverages()

# The minimal load average in the list.
min_load_avr = min([x[1] for x in load_avr_list])

# The list of available hosts with their number of free processors.
available_host_list = net.GetAvailableHosts()

# Gets the name of an available host.
available_host = net.GetAvailableHost()


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

# If you want to send a mail.
message = "This is just a test."
# net.SendMail(subject = '[netowrk.py]: Test', fromaddr = login@domail.com,
#              toadrr = login@domain.com, msg = message)
