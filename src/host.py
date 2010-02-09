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

"""\package host

Provides class 'Host' designed to manage host.
"""

import os, sys, commands
import socket, popen2


########
# HOST #
########


## It may be written in a temporary SSH configuration file.
_sshconfig_ = """
Host *
CheckHostIP no
NoHostAuthenticationForLocalhost yes
ChallengeResponseAuthentication no
"""


class Host:
    """Dedicated to host management."""


    def __init__(self, host = socket.gethostname(),
                 forced_ssh_config = False):
        """The constructor.
        Initializes the attributes and checks the SSH connection to the host.
        \param host The name of the host.
        """

        ## Name of the host.
        self.name = ""

        ## The number of processors.
        self.Nprocessor = 0

        ## The total memory.
        self.total_memory = 0

        ## The default SSH command.
        self.ssh = "ssh "
        if forced_ssh_config:
            if not os.path.isfile('/tmp/ssh-config-puppet'):
                file = open('/tmp/ssh-config-puppet', 'w')
                file.writelines(_sshconfig_)
                self.file_exit = 1
                file.close()
            self.ssh = "ssh -F /tmp/ssh-config-puppet "

        # Checks type argument.
        self.CheckArgument(host)

        # Checks SSH connection. Changed the SSH command if necessary.
        try:
            self.CheckSSH()
        except ValueError:
            if not os.path.isfile('/tmp/ssh-config-puppet'):
                file = open('/tmp/ssh-config-puppet', 'w')
                file.writelines(_sshconfig_)
                self.file_exit = 1
                file.close()
            self.ssh = "ssh -F /tmp/ssh-config-puppet "
            try:
                self.CheckSSH()
            except:
                print("ssh not work !")
                sys.exit(1)

        # Gets the number of processors.
        self.GetProcessorNumber()
        # Get the total memory.
        self.GetTotalMemory()


    def __del__(self):
        """The destructor.
        Deletes the temporary SSH configuration file.
        """
        if os.path.isfile('/tmp/ssh-config-puppet'):
            os.remove('/tmp/ssh-config-puppet')


    def CheckArgument(self, host):
        """Checks the argument.
        \param host The name of the host.
        """
        if isinstance(host, str):
            self.name = host
        elif isinstance(host, tuple):
            if len(host) != 2:
                raise ValueError, "The length of the tuple must be 2."
            if isinstance(host[0], str):
                self.name = host[0]
            else:
                raise ValueError, "The first element must be " \
                    + "the host name (str)."
            if not isinstance(host[-1], int) or host[-1] < 0:
                raise ValueError, "The number of processors must be " \
                    + "an integer strictly positive."
            else:
                self.Nprocessor = host[-1]
        elif isinstance(host, list):
            if len(host) != 2:
                raise ValueError, "The length of the list must be 2."
            if isinstance(host[0], str):
                self.name = host[0]
            else:
                raise ValueError, "The first element must be " \
                    + "the host name (str)."
            if not isinstance(host[-1], int) or host[-1] < 0:
                raise ValueError, "The number of processors must be " \
                    + "an integer strictly positive."
            else:
                self.Nprocessor = host[-1]
        else:
            raise ValueError, "The argument must be the host name (str)" \
                + ", a tuple (hostname, Ncpu) or a list [hostname, Ncpu]."


    def CheckSSH(self):
        """Checks the SSH connection.
        Launch a simple command via SSH (uptime). This command must be
        returned no error and just a single line.
        """
        if self.name == socket.gethostname():
            pass
        else:
            # Uptime test.
            command_name = self.ssh + self.name + " uptime"
            status, out = commands.getstatusoutput(command_name)
            if len(out.split('\n')) > 1:
                raise ValueError


    def GetProcessorNumber(self):
        """Returns the number of processors.
        @return An integer.
        """
        if self.Nprocessor != 0:
            return self.Nprocessor
        else:
            command_name = " cat /proc/cpuinfo | grep ^processor | wc -l"
            if self.name == socket.gethostname():
                status, out = commands.getstatusoutput(command_name)
                if status != 0:
                    self.RaiseErrorCommand(command_name, status, out)
                if len(out.split('\n')) != 1:
                    self.RaiseErrorCommand(command_name, status, out)
                self.Nprocessor = int(out)
            else:
                command_name = self.ssh + self.name + command_name
                status, out = commands.getstatusoutput(command_name)
                if status != 0:
                    self.RaiseErrorCommand(command_name, status, out)
                if len(out.split('\n')) != 1:
                    self.RaiseErrorCommand(command_name, status, out)
                self.Nprocessor = int(out)
            return self.Nprocessor


    def GetTotalMemory(self):
        """Returns the total memory (kB by default).
        @return A integer.
        """
        if self.total_memory != 0:
            return self.total_memory
        else:
            command_name = " cat /proc/meminfo | grep ^MemTotal " \
                + "| cut -d : -f 2"
            if self.name == socket.gethostname():
                status, out = commands.getstatusoutput(command_name)
                if status != 0:
                    self.RaiseErrorCommand(command_name, status, out)
                if len(out.split('\n')) != 1:
                    self.RaiseErrorCommand(command_name, status, out)
                self.total_memory = int(out.split()[0])
                return self.total_memory
            else:
                command_name = self.ssh + self.name + command_name
                status, out = commands.getstatusoutput(command_name)
                if status != 0:
                    self.RaiseErrorCommand(command_name, status, out)
                if len(out.split('\n')) != 1:
                    self.RaiseErrorCommand(command_name, status, out)
                self.total_memory = int(out.split()[0])
                return self.total_memory


    def GetUptime(self):
        """Returns the system load averages for the past (1, 5 and 15
        minutes).
        @return A list of floats or a string if the connection failed.
        """
        command_name = " uptime"
        if self.name == socket.gethostname():
            status, out = commands.getstatusoutput(command_name)
            if status != 0:
                self.RaiseErrorCommand(command_name, status, out)
            try:
                out = out.split()
                out = [float(x.strip(",")) for x in out[-3:]]
            except:
                # Connection failed?
                out = "off"
            return out
        else:
            command_name = self.ssh + self.name + command_name
            status, out = commands.getstatusoutput(command_name)
            if status != 0:
                self.RaiseErrorCommand(command_name, status, out)
            try:
                out = out.split()
                out = [float(x.strip(",")) for x in out[-3:]]
            except:
                # Connection failed?
                out = "off"
            return out


    def GetUsedMemory(self):
        """Returns the used memory (kB by default).
        @return An integer or a string if the connection failed.
        """
        command_name = " free | cut -d : -f 2"
        if self.name == socket.gethostname():
            status, out = commands.getstatusoutput(command_name)
            if status != 0:
                self.RaiseErrorCommand(command_name, status, out)
            try:
                out = out.split('\n')[2]
                out = int(out.split()[0])
            except:
                # Connection failed?
                out = "off"
            return out
        else:
            command_name = self.ssh + self.name + command_name
            status, out = commands.getstatusoutput(command_name)
            if status != 0:
                self.RaiseErrorCommand(command_name, status, out)
            try:
                out = out.split('\n')[2]
                out = int(out.split()[0])
            except:
                # Connection failed?
                out = "off"
            return out


    def RaiseErrorCommand(self, command_name, status, out):
        """Throws an exit message.
        """
        print("The command '%s' returns the status '%i'" %
              (command_name, status))
        print("with the message:")
        print("%s" % out)
        sys.exit(0)


    def LaunchInt(self, command):
        """Launches a command in interactive mode (using os.system).
        \param command The name of the command.
        @return The status of the command.
        """
        if self.name == socket.gethostname():
            return os.system(command)
        else:
            return os.system(self.ssh + self.name + ' ' + command)


    def LaunchFG(self, command):
        """Launches a command in the foreground.
        \param command The name of the command.
        @return The output and the status of the command in a tuple.
        """
        if self.name == socket.gethostname():
            return commands.getstatusoutput(command)
        else:
            return commands.getstatusoutput(self.ssh + self.name
                                            + ' ' + command)


    def LaunchBG(self, command):
        """Launches a command in the background and returns a Popen4 object.
        \param command The name of the command.
        @return A Popen4 object.
        """
        # Output is redirected.
        command = "( " + command + "; ) &> /dev/null"
        if self.name == socket.gethostname():
            return popen2.Popen4(command)
        else:
            return popen2.Popen4(self.ssh + self.name +
                                 " \"" + command + "\"")


    def LaunchWait(self, command, ltime, wait = 0.1):
        """Launches a command in the foreground and waits for its output for a
        given time after which the process is killed.

        \param command The name of the command.
        \param ltime The limit time.
        \param wait The waiting time.
        @return The output and the status of the command in a tuple.
        """
        import time
        # Output is redirected.
        file_index = 0
        while os.path.exists("/tmp/output-" + str(file_index)):
            file_index += 1
        file_tmp = open("/tmp/output-" + str(file_index), 'w')
        file_tmp.close()
        file_name = "/tmp/output-" + str(file_index)
        os.chmod(file_name, 0600)
        command = "( " + command + "; ) &> " + file_name
        p = popen2.Popen4(command)
        t = time.time()
        while (p.poll() == -1 and time.time() - t < ltime):
            time.sleep(wait)
        s = p.poll()
        if s == -1:
            try:
                os.kill(p.pid, 9)
            except:
                pass
        file_tmp = open(file_name, 'r')
        o = file_tmp.read()
        file_tmp.close()
        os.remove(file_name)
        return (s, o)
