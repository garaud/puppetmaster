# Copyright (C) 2009-2010 INRIA - EDF R&D
# Authors: Damien Garaud
#
# This file is part of the PuppetMaster project. It is an example for the
# module 'program_manager.py'.
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
import pwd
import socket
import time
import platform

from puppetmaster import program_manager


#######################
# Configuration Class #
#######################

print("""
#######################
# Configuration Class #
#######################""")

current_date = time.asctime()
username = pwd.getpwuid(os.getuid())[0]
computer = socket.gethostname()
tmp = platform.dist()
distribution = tmp[0] + '-' + tmp[1] + '_' + tmp[2]
# A dictionnary used in the replacement.
replacement = {'%date%': current_date,
               '%username%': username,
               '%computer%': computer,
               '%distribution%': distribution}
# An instance 'program_manager.Configuration'.
config = program_manager.Configuration('./example.cfg', mode = 'random',
                                       path = os.path.abspath('./'))
# Sets the replacement.
config.SetReplacementMap(replacement)
# Proceeds replacement.
config.Proceed()
print "The replacement is done."
print("See the file: \'" + config.file_list[0] \
          + "\' \nand compare it with \'" \
          + config.raw_file_list[0] + "\'.")
print "\nDo not forget to remove it."


#################
# Program Class #
#################

print("""\n
#################
# Program Class #
#################""")

# Declaration.
command_name = '/bin/ls'
program = program_manager.Program(command_name)

# Name of the command.
cmd = program.Command()
print "Command: ", cmd

# Tries the program.
program.Try()

# Launches the program.
program.Run()
print "Information about the program:\n\n", program.log


########################
# ProgramManager Class #
########################

print("""\n
########################
# ProgramManager Class #
########################""")

# Declaration.
group_ = 0
command_list = ['/bin/ls', '/bin/pwd', '/bin/ps']
program_ensemble = program_manager.ProgramManager()
for name in command_list:
    prg = program_manager.Program(name, group = group_)
    program_ensemble.AddProgram(prg)
    group_ += 1

# Runs the ensemble of programs.
print 'Runs.'
program_ensemble.Run()

# Runs the ensemble of programs on remote hosts (thanks to 'network.py').
print "\nRuns on remote hosts."
program_ensemble.RunNetwork(delay = 2.)
