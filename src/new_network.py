# Copyright (C) 2005-2010 INRIA - EDF R&D
# Authors: Vivien Mallet, Damien Garaud
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

"""\package network

Provides class 'Network' designed to managed processes launched over the
network.
"""

import os, sys, types, commands, string, pwd
import socket, popen2
import threading
import host


###########################
# MISCELLANEOUS FUNCTIONS #
###########################


def IsNum(str):
    """Is the string is a float?
    \param str a string
    @return 0 or 1
    """
    is_num = 1
    try:
        num = float(str)
    except ValueError:
        is_num = 0
    return is_num


def IsInt(str):
    """Tests whether a string is an integer.
    \param str a string to be tested.
    @return True if 'str' is a integer, False otherwise.
    """
    is_num = True
    try:
        num = int(str)
    except ValueError:
        is_num = False
    return is_num


def ToNum(str):
    """Converts a string to a number.
    \param str a string to be converted.
    @return The number represented by 'str'.
    """
    if IsInt(str):
        return int(str)
    elif IsNum(str):
        return float(str)
    else:
        raise Exception, "\"" + str + "\" is not a number."


def remove(files):
    """Removes one or more files and/or directories."""
    if isinstance(files, str):
        files = [files]
    if not isinstance(files, list):
        raise ValueError
    for file in files:
        import os
        if os.path.isdir(file):
            import shutil
            shutil.rmtree(file)
        elif os.path.isfile(file):
            os.remove(file)


###########
# NETWORK #
###########


class Network:
    """Dedicated to network management."""


    def __init__(self, host_list = None):
        """Initiliazes the list of hosts.
        \param host_list A list of host instances, host names or a file.
        """

        ## The hosts list.
        self.hosts = []

        self.CheckArgument(host_list)

        # Empty connected hosts list?
        if self.GetConnectedHostNumber() == 0:
            raise ValueError, "The list of connected hosts list is empty."


    def CheckArgument(self, host_list):
        """Checks the argument.
        \param host_list A list of host instances, host names or a file.
        """
        if host_list == None:
            self.hosts = [host.Host(socket.gethostname())]
            pass
        elif isinstance(host_list, list):
            if len(host_list) == 0:
                raise ValueError, "The hosts list is empty."
            if isinstance(host_list[0], str):
                self.GetThreadHost(host_list)
            elif host_list[0].__class__ == host.Host:
                for instance in host_list:
                    self.hosts.append(instance)
            else:
                raise ValueError, "The element of the list must be " \
                    + " host names (str) or host instances (host.Host)."
        elif isinstance(host_list, str):
            if os.path.isfile(host_list):
                file = open(host_list, 'r')
                out = file.readlines()
                file.close()
                if len(out) == 0:
                    raise ValueError, "The file '%s' is empty." % host_list
                host_list = []
                for hostname in out:
                    host_list.append(hostname.strip())
                self.GetThreadHost(host_list)
            else:
                raise ValueError, "The file '%s' not found." % host_list
        else:
            raise ValueError, "The argument must be a list of hosts" \
                + " or a file."


    def SetHostList(self, host_list):
        """Sets a new list of hosts.
        \param host_list A list of host instances, host names or a file.
        """
        self.hosts = []
        self.CheckArgument(host_list)
        # Empty connected hosts list?
        if self.GetConnectedHostNumber() == 0:
            raise ValueError, "The list of connected hosts list is empty."


    def PrintHostNames(self):
        """Prints the name of hosts.
        """
        for host in self.hosts:
            print host.name


    def GetHostNames(self):
        """Returns the hosts names.
        @return The list of hosts.
        """
        result = []
        for host in self.hosts:
            result.append(host.name)
        return result


    def GetNhost(self):
        """Returns the number of hosts.
        @return Number of hosts.
        """
        return len(self.hosts)


    def GetConnectedHostNumber(self):
        """Returns the number of well connected hosts.
        @return Number of connected hosts.
        """
        count = 0
        for host in self.hosts:
            if host.connection:
                count += 1
        return count


    def GetProcessorNumber(self):
        """
        """
        result = []
        for host in self.hosts:
            result.append((host.name, host.Nprocessor))
        return result


    def GetThreadHost(self, host_list):
        """
        """
        processus_list = []
        # Launches all threads.
        for hostname in host_list:
            if len(hostname) != 0:
                thread_host = ThreadHost(hostname)
                processus_list.append(thread_host)
                thread_host.start()
        # Gets the results.
        for processus in processus_list:
            processus.join()
            self.hosts.append(processus.host_instance)


    def GetUptime(self):
        """
        """
        processus_list = []
        result = []
        # Launches all threads.
        for host_instance in self.hosts:
            thread_uptime = ThreadUptime(host_instance)
            processus_list.append(thread_uptime)
            thread_uptime.start()
        # Gets the results.
        for processus in processus_list:
            processus.join()
            result.append((processus.hostname, processus.uptime))
        return result


    def GetUsedMemory(self):
        """
        """
        processus_list = []
        result = []
        # Launches all threads.
        for host_instance in self.hosts:
            thread_memory = ThreadUsedMemory(host_instance)
            processus_list.append(thread_memory)
            thread_memory.start()
        # Gets the results.
        for processus in processus_list:
            processus.join()
            result.append((processus.hostname, processus.used_memory))
        return result


    def GetAvailableHosts(self):
        """Returns the available hosts.
        @return a list of hosts in a tuple with the number of available
        cpu. The computation is done with the system load averages for the
        past 1 minute. See the Unix command 'uptime'.
        """
        uptime_list = self.GetUptime()
        result = []
        # A loop for every hosts to pick up the number of available cpu.
        for host in self.hosts:
            index = [x[0] for x in uptime_list].index(host.name)
            average = uptime_list[index][1][0]
            if average < host.Nprocessor - 0.5 and average != 'off':
                result.append((host.name, int(host.Nprocessor
                                              - average + 0.5)))
        return result


###################
# THREADING CLASS #
###################

class ThreadHost(threading.Thread):
    """
    """
    def __init__(self, hostname):
        threading.Thread.__init__(self)
        self.hostname = hostname
    def run(self):
        self.host_instance = host.Host(self.hostname)


class ThreadUptime(threading.Thread):
    """
    """
    def __init__(self, host):
        threading.Thread.__init__(self)
        self.host = host
        self.hostname = self.host.name
    def run(self):
        self.uptime = self.host.GetUptime()


class ThreadUsedMemory(threading.Thread):
    """
    """
    def __init__(self, host):
        threading.Thread.__init__(self)
        self.host = host
        self.hostname = self.host.name
    def run(self):
        self.used_memory = self.host.GetUsedMemory()




#     def LaunchInt(self, command, host = socket.gethostname()):
#         """Launches a command in interactive mode (using os.system).

#         \param command the name of the command.
#         \param host the name of the host.
#         @return the status of the command.
#         """
#         if not isinstance(host, Host):
#             host = Host(host)
#         if host.name == socket.gethostname():
#             return os.system(command)
#         else:
#             return os.system(ssh + host.name + " \"" + command + "\"")


#     def LaunchFG(self, command, host = socket.gethostname()):
#         """Launches a command in the foreground.

#         \param command the name of the command.
#         \param host the name of the host.
#         @return the output and the status of the command.
#         """
#         if not isinstance(host, Host):
#             host = Host(host)
#         if host.name == socket.gethostname():
#             (s, o) = commands.getstatusoutput(command)
#             # # "commands.getstatusoutput" removes the last '\n' if it exists!
#             # # Assuming that there was a line break:
#             # o += "\n"
#         else:
#             (s, o) = commands.getstatusoutput(ssh + host.name \
#                                               + " \"" + command + "\"")
#         # Note: "commands.getstatusoutput" removes the last '\n' if it exists!
#         return (s, o)


#     def LaunchWait(self, command, ltime, wait = 0.1,
#                    host = socket.gethostname()):
#         """Launches a command in the foreground and waits for its output for a given
#         time after which the process is killed.

#         \param command the name of the command.
#         \param ltime the limit time.
#         \param wait the waiting time.
#         \param host the name of the host.
#         @return the output and the status of the command.
#         """
#         import time
#         if not isinstance(host, Host):
#             host = Host(host)
#         # Output is redirected.
#         file_index = 0
#         while os.path.exists("/tmp/output-" + str(file_index)):
#             file_index += 1
#         file_tmp = open("/tmp/output-" + str(file_index), 'w')
#         file_tmp.close()
#         file_name = "/tmp/output-" + str(file_index)
#         os.chmod(file_name, 0600)
#         if host.name == socket.gethostname():
#             command = "( " + command + "; ) &> " + file_name
#         else:
#             command = "( " + ssh + " " + host.name + " \"" \
#                       + command + "\"; ) &> " + file_name
#         p = popen2.Popen4(command)
#         t = time.time()
#         while (p.poll() == -1 and time.time() - t < ltime):
#             time.sleep(wait)
#         s = p.poll()
#         if s == -1:
#             try:
#                 os.kill(p.pid, 9)
#             except:
#                 pass
#         o = open("/tmp/output-" + str(file_index), 'r').read()
#         os.remove(file_name)
#         return (s, o)


#     def LaunchBGTest(self):
#         """Checks the LaunchBG function on all hosts."""
#         command = "/bin/ls"
#         proc = []
#         for h in self.hosts:
#             proc.append(self.LaunchBG(command, h))
#         for p in proc:
#             if p.poll() != 0 and p.poll() != -1:
#                 raise Exception, "An error appears during the launching of " \
#                       + "the command \"" + command + "\" on host \"" \
#                       + h.name + "\"."


#     def LaunchBG(self, command, host = socket.gethostname()):
#         """Launches a command in the background and returns a Popen4 object.

#         \param command the name of the command.
#         \param host the name of the host.
#         @return a Popen4 object.
#         """
#         import os
#         if not isinstance(host, Host):
#             host = Host(host)
#         # Output is redirected.
#         command = "( " + command + "; ) &> /dev/null"
#         if host.name == socket.gethostname():
#             return popen2.Popen4(command)
#         else:
#             return popen2.Popen4(ssh + host.name + " \"" + command + "\"")


#     def LaunchScreen(self, command, host = socket.gethostname()):
#         """Launches a command in a screen.
        
#         \param command the name of the command.
#         \param host the name of the host.
#         """
#         if not isinstance(host, Host):
#             host = Host(host)
#         if host.name != socket.gethostname():
#             command = ssh + host.name + " screen -d -m " + command
#         else:
#             command = "screen -d -m " + command
#         os.system(command)


#     def SendMail(self, subject, fromaddr, toaddr, msg = ""):
#         """Sends a mail.
#         """
#         from email.MIMEText import MIMEText
#         msg = MIMEText(msg)
#         msg['Subject'] = subject
#         msg['From'] = fromaddr
#         msg['To'] = toaddr
#         import smtplib
#         server = smtplib.SMTP('localhost')
#         server.sendmail(fromaddr, toaddr, msg.as_string())
#         server.quit()


#     def SendMailAttach(self, subject, attachments, fromaddr, toaddr,
#                        msg = ""):
#         """Sends a mail with attachments.
#         """
#         from email.MIMEMultipart import MIMEMultipart
#         from email.MIMEText import MIMEText
#         tmp = MIMEMultipart()
#         tmp.attach(MIMEText(msg))
#         msg = tmp
#         msg['Subject'] = subject
#         msg['From'] = fromaddr
#         msg['To'] = toaddr
#         if type(attachments) == types.StringType:
#             file = open(attachments, 'rb')
#             msg.attach(MIMEText(file.read()))
#             file.close()
#         else:
#             for attachment in attachments:
#                 file = open(attachment, 'rb')
#                 msg.attach(MIMEText(file.read()))
#                 file.close()
#         import smtplib
#         server = smtplib.SMTP('localhost')
#         server.sendmail(fromaddr, toaddr, msg.as_string())
#         server.quit()


#     def GetLoadAverages(self):
#         """Returns the load averages.

#         @return a list of hosts with the load averages for the past 1 minute.
#         """
#         result = []
#         command = "dsh -r " + ssh + " -Mc -g "+ self.group \
#             + " 'echo `hostname` `uptime`'"
#         status, out = commands.getstatusoutput(command)
#         # If the command does not work.
#         if status != 0:
#             raise Exception, "Unable to launch the command: \"" + command \
#                   + "\"."
#         # A loop for every hosts to pick the load averages.
#         for line in out.split("\n"):
#             name = line.split()[0].strip(':')
#             load_average = ToNum(line.split()[-3].strip(','))
#             result.append((name, load_average))
#         return result


#     def GetAvailableHosts(self):
#         """Returns the available hosts.

#         @return a list of hosts with the number of available cpu.
#         """
#         # The network load averages.
#         host_avr = self.GetLoadAverages()
#         result = []
#         # A loop for every hosts to pick up the number of available cpu.
#         for host in self.hosts:
#             index = [x[0] for x in host_avr].index(host.name)
#             avr = host_avr[index][1]
#             if avr < host.cpu - 0.5:
#                 result.append((host.name, int(host.cpu - avr + 0.5)))
#         return result
    
        
#     def GetAvailableHost(self, load_limit = 0.3):
#         """Return an available host.
        
#         \param load_limit the limit time to load.
#         @return an available host or the host with the minimal load averages.
#         """
#         import time
#         result = ""
#         host_list = self.GetLoadAverages()
#         for host in host_list:
#             if host[1] <= load_limit:
#                 result = host[0]
#         if len(result) == 0:
#             load_list = [x[1] for x in host_list]
#             load_min = min(load_list)
#             result = self.hosts[load_list.index(load_min)].name
#         return result
            

#     def GetRandomAvailableHost(self, load_limit = 0.3):
#         """Returns a random available host.

#         \param load_limit the limit time to load.
#         @return the name of a random available host.
#         """
#         host_available = []
#         for host in self.hosts:
#             l = host.LoadAverage()[0]
#             if l < load_limit:
#                 host_available.append(host)
#         if len(host_available) != 0:
#             import random
#             return host_available[random.randint(0, len(host_available) - 1)].name
#         else:
#             return self.hosts[0].name


# if __name__ == "__main__":
#     ## A network.Network instance.
#     net = Network()
#     print "# Name \t # CPU"
#     for host in net.hosts:
#         print(host.name + '\t' + str(host.cpu))
