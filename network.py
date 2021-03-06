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

\author Vivien Mallet, Damien Garaud
"""

import os
import types
import socket
import threading

from puppetmaster import host


###########################
# MISCELLANEOUS FUNCTIONS #
###########################


def is_num(str_):
    """Is the string is a float?
    \param str a string
    @return 0 or 1
    """
    is_num_ = 1
    try:
        num = float(str_)
    except ValueError:
        is_num_ = 0
    return is_num_


def is_int(str_):
    """Tests whether a string is an integer.
    \param str a string to be tested.
    @return True if 'str' is a integer, False otherwise.
    """
    is_num_ = True
    try:
        num = int(str_)
    except ValueError:
        is_num_ = False
    return is_num_


def to_num(str_):
    """Converts a string to a number.
    \param str a string to be converted.
    @return The number represented by 'str'.
    """
    if is_int(str_):
        return int(str_)
    elif is_num(str_):
        return float(str_)
    else:
        raise Exception, "\"" + str + "\" is not a number."


def remove(files):
    """Removes one or more files and/or directories."""
    if isinstance(files, str):
        files = [files]
    if not isinstance(files, list):
        raise ValueError
    for filename in files:
        if os.path.isdir(filename):
            import shutil
            shutil.rmtree(filename)
        elif os.path.isfile(filename):
            os.remove(filename)


###########
# NETWORK #
###########


class Network:
    """Dedicated to network management.
    It contains a list of 'host.Host' instances.
    """


    def __init__(self, host_list = None, forced_ssh_config = False):
        """Initiliazes the list of hosts.
        \param host_list A list of host instances, host names or a file.
        \param forced_ssh_config Would like to use the PuppetMaster SSH
        configuration? (True or False). See the variable 'host.__sshconfig__'.
        """

        ## The hosts list.
        self.hosts = []

        self.CheckArgument(host_list, forced_ssh_config)

        # Empty connected hosts list?
        if self.GetConnectedHostNumber() == 0:
            raise ValueError, "The list of connected hosts list is empty."


    def CheckArgument(self, host_list, forced_ssh_config):
        """Checks the argument.
        \param host_list A list of host instances, host names or a file.
        \param forced_ssh_config Would like to use the PuppetMaster SSH
        configuration? (True or False). See the variable 'host.__sshconfig__'.
        """
        # The local host by default.
        if host_list == None:
            self.hosts = [host.Host(socket.gethostname())]
        # A list of hosts (name or instance).
        elif isinstance(host_list, list):
            self.CheckArgumentHostList(host_list, forced_ssh_config)
        # A file with the list of host names
        elif isinstance(host_list, str):
            self.CheckArgumentHostFile(host_list, forced_ssh_config)
        else:
            raise ValueError, "The argument must be a list of hosts" \
                + " or a file."


    def CheckArgumentHostList(self, host_list, forced_ssh_config):
        """Checks the main argument if it is a list of hosts.
        """
        if len(host_list) == 0:
            raise ValueError, "The hosts list is empty."
        if isinstance(host_list[0], str):
            self.GetThreadHost(host_list, forced_ssh_config)
        elif isinstance(host_list[0], host.Host):
            for instance in host_list:
                self.hosts.append(instance)
        else:
            raise ValueError, "The element of the list must be " \
                + " host names (str) or host instances (host.Host)."


    def CheckArgumentHostFile(self, host_list, forced_ssh_config):
        """Checks the main argument if it is a file.
        """
        if os.path.isfile(host_list):
            # Reading.
            hostfile = open(host_list, 'r')
            out = hostfile.readlines()
            hostfile.close()
            if len(out) == 0:
                raise ValueError, "The file '%s' is empty." % host_list
            host_list = []
            # Loop on host names in the file.
            for hostname in out:
                host_list.append(hostname.strip())
            self.GetThreadHost(host_list, forced_ssh_config)
        else:
            raise ValueError, "The file '%s' not found." % host_list


    def SetHostList(self, host_list, forced_ssh_config):
        """Sets a new list of hosts.
        \param host_list A list of host instances, host names or a file.
        """
        self.hosts = []
        self.CheckArgument(host_list, forced_ssh_config)
        # Empty connected hosts list?
        if self.GetConnectedHostNumber() == 0:
            raise ValueError, "The list of connected hosts list is empty."


    def PrintHostNames(self):
        """Prints the name of hosts.
        """
        for host_ in self.hosts:
            print host_.name


    def GetHostNames(self):
        """Returns the hosts names.
        @return The list of host names.
        """
        result = []
        for host_ in self.hosts:
            result.append(host_.name)
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
        for host_ in self.hosts:
            if host_.connection:
                count += 1
        return count


    def GetProcessorNumber(self):
        """Returns the number or cpu for each host.
        @return A list of tuples (hostname, Nprocessor)
        """
        result = []
        for host_ in self.hosts:
            result.append((host_.name, host_.Nprocessor))
        return result


    def GetThreadHost(self, host_list, forced_ssh_config = False):
        """Creates 'host.Host' instances with multi-threading.
        \param host_list A list of host names.
        \param forced_ssh_config Would like to use the PuppetMaster SSH
        configuration? (True or False). See the variable 'host.__sshconfig__'.
        """
        processus_list = []
        # Launches all threads.
        for hostname in host_list:
            if len(hostname) != 0:
                thread_host = ThreadHost(hostname, forced_ssh_config)
                processus_list.append(thread_host)
                thread_host.start()
        # Gets the results.
        for processus in processus_list:
            processus.join()
            self.hosts.append(processus.host_instance)


    def GetUptime(self):
        """Returns the output of the Unix command 'uptime' for each host.
        Launches the command 'uptime' to each host with multi-threading.
        @return A list of tuples (hostname, uptime).
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
        """Returns the used memory for each host (kB).
        Launches the Unix command 'free' to each host with multi-threading.
        @return A list of tuples (hostname, used memory).
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
        @return A list of tuples (hostname, available cpu).
        """
        uptime_list = self.GetUptime()
        result = []
        # A loop for every hosts to pick up the number of available cpu.
        for host_ in self.hosts:
            index = [x[0] for x in uptime_list].index(host_.name)
            if host_.connection:
                average = uptime_list[index][1][0]
                if average < host_.Nprocessor - 0.5:
                    result.append((host_.name, int(host_.Nprocessor
                                                   - average + 0.5)))
        return result


    def BusySoWait(self, wait_time = 5.):
        """Checks the available hosts and waits if necessary.
        When the list of available hosts is not empty, returns the list of
        available host, waits for an available host while the list is empty.
        \param wait_time Waiting time until a new checking of available hosts
        (in seconds).
        @return A list of tuples (hostname, available cpu).
        """
        import time
        host_list = self.GetAvailableHosts()
        while len(host_list) == 0:
            time.sleep(wait_time)
            host_list = self.GetAvailableHosts()
        return host_list


    def LaunchInt(self, command, host_ = socket.gethostname()):
        """Launches a command in interactive mode (using os.system).
        \param command The name of the command.
        \param host_ The name of the host or a 'host.Host' instance.
        @return The status of the command.
        """
        # The name of a host.
        if isinstance(host_, str):
            if host_ not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not found " % host_ \
                    + "in the list of hosts."
            index = [x.name for x in self.hosts].index(host_)
            return self.hosts[index].LaunchInt(command)
        # A 'Host' instance.
        if isinstance(host_, host.Host):
            if host_.name not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not " % host_.name \
                    + "found in the list of hosts."
            return host_.LaunchInt(command)


    def LaunchFG(self, command, host_ = socket.gethostname()):
        """Launches a command in the foreground.
        \param command The name of the command.
        \param host_ The name of the host or a 'host.Host' instance.
        @return The output and the status of the command in a tuple.
        """
        # The name of a host.
        if isinstance(host_, str):
            if host_ not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not found " % host_ \
                    + "in the list of hosts."
            index = [x.name for x in self.hosts].index(host_)
            return self.hosts[index].LaunchFG(command)
        # A 'Host' instance.
        if isinstance(host_, host.Host):
            if host_.name not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not " % host_.name \
                    + "found in the list of hosts."
            return host_.LaunchFG(command)


    def LaunchBG(self, command, host_ = socket.gethostname()):
        """Launches a command in the background.
        \param command The name of the command.
        \param host_ The name of the host or a 'host.Host' instance.
        @return A Popen4 object.
        """
        if isinstance(host_, str):
            if host_ not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not found " % host_ \
                    + "in the list of hosts."
            index = [x.name for x in self.hosts].index(host_)
            return self.hosts[index].LaunchBG(command)
        if isinstance(host_, host.Host):
            if host_.name not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not " % host_.name \
                    + "found in the list of hosts."
            return host_.LaunchBG(command)


    def LaunchSubProcess(self, command, host_ = socket.gethostname(),
                         out_option = None):
        """Launches a command in the background with the module 'subprocess'.
        The standard output and error can be called with
        'subprocess.Popen.communicate()' method when the process terminated.
        \param command The name of the command.
        \param host_ The name of the host or a 'host.Host' instance.
        \param outo_ption A string.
          - None: writes the standard output in '/dev/null'.
          - 'pipe': writes the standard output in the 'subprocess.PIPE'
          - 'file': writes the standard output in file such as
            '/tmp/hostname-erTfZ'.
        Be careful, if the standard output is too long, the PIPE will be full
        and the subprocess will stop (not be killed, but just stop).
        @return A 'subprocess.Popen' instance or (file object,
        subprocess.Popen) when the 'out_option' is set to 'file'.
        """
        if isinstance(host_, str):
            if host_ not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not found " % host_ \
                    + "in the list of hosts."
            index = [x.name for x in self.hosts].index(host_)
            return self.hosts[index].LaunchSubProcess(command, out_option)
        if isinstance(host_, host.Host):
            if host_.name not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not " % host_.name \
                    + "found in the list of hosts."
            return host_.LaunchSubProcess(command, out_option)


    def LaunchWait(self, command, ltime, wait = 0.1,
                   host_ = socket.gethostname()):
        """Launches a command in the background and waits for its output for a
        given time after which the process is killed.
        \param ltime The limit time.
        \param wait The waiting time.
        \param command The name of the command.
        \param host_ The name of the host or a 'host.Host' instance.
        @return The output and the status of the command in a tuple.
        """
        if isinstance(host_, str):
            if host_ not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not found " % host_ \
                    + "in the list of hosts."
            index = [x.name for x in self.hosts].index(host_)
            return self.hosts[index].LaunchWait(command, ltime, wait)
        if isinstance(host_, host.Host):
            if host_.name not in [x.name for x in self.hosts]:
                raise ValueError, "The host name '%s' not " % host_.name \
                    + "found in the list of hosts."
            return host_.LaunchWait(command, ltime, wait)


    def SendMail(self, subject, fromaddr, toaddr, msg = ""):
        """Sends a mail.
        \param subject The subject
        \param fromaddr The email address of the sender.
        \param toaddr The email address of the recipient.
        \param msg The message.
        """
        import smtplib
        from email.mime.text import MIMEText
        message = MIMEText(msg)
        message['Subject'] = subject
        message['From'] = fromaddr
        message['To'] = toaddr
        server = smtplib.SMTP('localhost')
        server.sendmail(fromaddr, toaddr, message.as_string())
        server.quit()


    def SendMailAttach(self, subject, attachments, fromaddr, toaddr,
                       msg = ""):
        """Sends a mail with attachments.
        \param subject The subject
        \param attachments A file or a list of files.
        \param fromaddr The email address of the sender.
        \param toaddr The email address of the recipient.
        \param msg The message.
        """
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        message = MIMEMultipart()
        message.attach(MIMEText(msg))
        message['Subject'] = subject
        message['From'] = fromaddr
        message['To'] = toaddr
        if type(attachments) == types.StringType:
            attach_file = open(attachments, 'rb')
            message.attach(MIMEText(attach_file.read()))
            attach_file.close()
        else:
            for attachment in attachments:
                attach_file = open(attachment, 'rb')
                message.attach(MIMEText(attach_file.read()))
                attach_file.close()
        server = smtplib.SMTP('localhost')
        server.sendmail(fromaddr, toaddr, message.as_string())
        server.quit()


###################
# THREADING CLASS #
###################

class ThreadHost(threading.Thread):
    """A derived class of 'threading.Thread'.
    It is used to declare a list of hosts with multi-threading.
    """
    def __init__(self, hostname, forced_ssh_config = False):
        """The constructor.
        \param hostname A name of host.
        \param forced_ssh_config Would like to use the PuppetMaster SSH
        configuration? (True or False). See the variable 'host.__sshconfig__'.
        """
        threading.Thread.__init__(self)
        ## The host name.
        self.hostname = hostname
        ## PuppetMaster SSH configuration?
        self.forced_ssh_config = forced_ssh_config
    def run(self):
        """Runs the thread.
        """
        ## The 'host' instance.
        self.host_instance = host.Host(self.hostname, self.forced_ssh_config)


class ThreadUptime(threading.Thread):
    """A derived class of 'threading.Thread'.
    It is used to launch the Unix command 'uptime' to a list of hosts with
    multi-threading.
    """
    def __init__(self, host):
        """The constructor.
        \param host A 'host.Host' instance.
        """
        threading.Thread.__init__(self)
        ## The 'host' instance.
        self.host = host
        ## The host name.
        self.hostname = self.host.name
    def run(self):
        """Runs the thread.
        """
        ## A list of floats or a string if the connection failed.
        self.uptime = self.host.GetUptime()


class ThreadUsedMemory(threading.Thread):
    """A derived class of 'threading.Thread'.
    It is used to launch the Unix command 'free' to a list of hosts with
    multi-threading.
    """
    def __init__(self, host):
        """The constructor.
        \param host A 'host.Host' instance.
        """
        threading.Thread.__init__(self)
        ## The 'host' instance.
        self.host = host
        ## The host name.
        self.hostname = self.host.name
    def run(self):
        """Runs the thread.
        """
        ## An integer or a string if the connection failed.
        self.used_memory = self.host.GetUsedMemory()
