# Copyright (C) 2006-2010, ENPC - INRIA - EDF R&D
#     Author(s): Vivien Mallet, Damien Garaud
#
# This file is part of the PuppetMaster project. It provides facilities to
# launch several programs with or without configuration files.
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

"""\package src.program_manager

This module provides facilities to launch several programs.

Class list:
 <ul>
  <li>ProgramManager</li>
  <li>Program</li>
  <li>Configuration</li>
 </ul>

\author Vivien Mallet, Damien Garaud
"""

import host
import network

###################
# PROGRAM_MANAGER #
###################


class ProgramManager:
    """This class manages the execution of several programs.
    """


    def __init__(self, net = network.Network()):
        """Initializes the network and the logs.
        \param net The network over which the simuations should be launched.
        """
        ## The list of programs.
        self.program_list = []

        ## A string.
        self.log = "-" * 78 + "\n\n"

        ## The list of processes.
        self.process = []

        ## A 'network.Network' instance.
        self.net = net


    def GetLog(self):
        """Returns the log.
        @return Simulation logs.
        """
        return self.log


    def SetNetwork(self, net = network.Network()):
        """Sets the network.
        \param net The network over which the simuations should be launched.
        """
        self.net = net


    def AddProgram(self, program):
        """Adds a program.
        \param program The program to be added.
        """
        if isinstance(program, str):
            self.program_list.append(Program(program))
        else:
            self.program_list.append(program)
        def compare(x, y):
            if x.group < y.group:
                return -1
            elif x.group > y.group:
                return 1
            else:
                return 0
        self.program_list.sort(compare)


    def Clear(self):
        """Clears all; primarily, the program list and the logs.
        """
        self.program_list = []
        self.log = "-" * 78 + "\n\n"


    def Run(self):
        """Executes the set of programs on localhost.
        """
        if len(self.program_list) == 0:
            raise Exception, "The program list is empty."
        for program in self.program_list:
            print "Program name: ", program.name.split("/")[-1]
            program.Run()
            self.log += program.log
            if self.log[-1] != "\n":
                self.log += "\n"
            self.log += "\n" + "-" * 78 + "\n\n"
            if program.status != 0:
                print self.log
                raise Exception, "Program \"" + program.basename \
                      + "\" failed."


    def RunNetwork(self, delay = 2., buzy_time = 10., wait_time = 10.,
                   out_option = None):
        """Executes the set of programs on the network.
        \param delay The minimum period of time between the launching of two
        programs. Unit: seconds.
        \param buzy_time The waiting time before checking a new available
        hosts.
        \param wait_time The waiting time before the end of a group of
        programs.
        \param outoption A string.
          - None: writes the standard output in '/dev/null'.
          - 'pipe': writes the standard output in the 'subprocess.PIPE'
          - 'file': writes the standard output in file such as
            '/tmp/puppet-hostname-erTfZ'.
        """
        import time, commands, copy
        if len(self.program_list) == 0:
            raise Exception, "The program list is empty."
        self.process = []
        host = []
        self.output_file_list = []
        already_dead = [False for i in range(len(self.program_list))]
        beg_time = []
        end_time = ["" for i in range(len(self.program_list))]
        # Index of the first program from current group.
        i_group = 0
        count_program = 1
        count_host = 0
        # List of available hosts (tuple: (hostname, Ncpu))
        host_available = self.net.GetAvailableHosts()
        Ncpu_list = [x[1] for x in host_available]
        # Sum of available cpus.
        Ncpu = sum(Ncpu_list)
        cpu_cumsum = [sum(Ncpu_list[0:x + 1]) for x in range(len(Ncpu_list))]
        # Copies and replaces for configuration files.
        for i in range(len(self.program_list)):
            program = self.program_list[i]
            program.config.Proceed()
        self.log += "Available host %s\n" % str(host_available)
        self.log += "Cumulative sum %s\n" % str(cpu_cumsum)
        self.log += "Ncpu %s\n" % Ncpu
        # Program runs on Network.
        for i in range(len(self.program_list)):
            program = self.program_list[i]
            self.log += '-' * 78 + '\n'
            self.log += "Program index %i\n" % i
            self.log += "Program Command '%s'\n" % program.Command()
            self.log += "First index program Group '%i'\n" % i_group
            if i > i_group and program.group != self.program_list[i-1].group:
                # If any process from the previous group is still up.
                while None in [x.poll() for x in self.process[i_group:]]:
                    time.sleep(wait_time)
                i_group = i
                count_program = 1
                count_host = 0
                host_available = self.net.GetAvailableHosts()
                Ncpu_list = [x[1] for x in host_available]
                Ncpu = sum(Ncpu_list)
                cpu_cumsum = [sum(Ncpu_list[0:x + 1]) for x \
                              in range(len(Ncpu_list))]
            # If all hosts are busy.
            if count_program > Ncpu:
                self.log += " --- Host Busy ---\n"
                time.sleep(buzy_time)
                host_available = self.net.BusySoWait(buzy_time)
                count_host = 0
                count_program = 1
                Ncpu_list = [x[1] for x in host_available]
                Ncpu = sum(Ncpu_list)
                cpu_cumsum = [sum(Ncpu_list[0:x + 1]) for x \
                              in range(len(Ncpu_list))]
                self.log += "\tNew hosts list.\n"
                self.log += '\t' + str(host_available) + ' \n'
                self.log += "\tcpu_cum_sum %s\n" % str(cpu_cumsum)
                self.log += "\tNcpu %i\n" % Ncpu
                self.log += " --- End Host Busy ---\n"

            # Changes host.
            self.log += "Count program %i\n" % count_program
            self.log += "Count host %i\n" % count_host
            self.log += "Length cpu_cumsum %i\n" % len(cpu_cumsum)
            self.log += "Index cpu cumulative sum %i\n" % cpu_cumsum[count_host]
            if count_program > cpu_cumsum[count_host]:
                count_host += 1
                self.log += "Changed Host."
                self.log += "Count host %i\n" % count_host
            current_host = host_available[count_host][0]
            self.log += "Current host name '%s'\n" % current_host

            # Launches the subprocess.
            print "Program: ", program.basename, \
                " - Available host: ", current_host
            if out_option == 'file':
                outfile, p = self.net.LaunchSubProcess(program.Command(),
                                                       current_host,
                                                       out_option)
                self.output_file_list.append(outfile)
            else:
                p = self.net.LaunchSubProcess(program.Command(),
                                              current_host)
            self.log += "Sub-program with the ID %i\n" % p.pid
            self.process.append(p)
            count_program += 1
            host.append(current_host)
            beg_time.append(time.asctime())

            # If processus is done, writes the ended date.
            for j in range(i):
                if end_time[j] == "" and self.process[j].poll() != None:
                    end_time[j] = time.asctime()

            # Checks current process status.
            i_proc = copy.copy(i_group)
            # Loop on current running subprocess.
            for subproc in self.process[i_group:]:
                if subproc.poll() != None and subproc.wait() != 0:
                    if not already_dead[i_proc]:
                        std_message = subproc.communicate()
                        warning_message = "\n\rWARNING: The program: \"" \
                            + self.program_list[i_proc].Command() \
                            + "\" does not work on the host '" \
                            + host[i_proc]  + "'.\n"\
                            + "status: " + str(subproc.wait()) \
                            + "\n\nOutput message:" \
                            + " \n  STDOUT: " + str(std_message[0]) \
                            + " \n  STDERR: " + str(std_message[1])
                        if out_option == 'file':
                            warning_message += "\n\rSee the file '" \
                                + self.output_file_list[i_proc].name \
                                + "' to read the standard output."
                            try:
                                self.output_file_list[i_proc].close()
                            except:
                                pass
                        self.log += warning_message
                        print warning_message
                        print "\n\rThe other sub-processus are still" \
                            + " running...\n"
                        already_dead[i_proc] = True
                i_proc += 1
            # Wainting time.
            time.sleep(delay)
        # End for program launching.

        # Waits for the latest programs.
        self.log += "\nWaits for the lastet programs.\n"
        self.log += "First index program Group '%i'\n" % i_group
        #while None in [x.returncode for x in self.process[i_group:]]:
        count_wait = 0
        while None in [x.poll() for x in self.process[i_group:]]:
            time.sleep(delay)
            count_wait += 1
            self.log += "Clock: " + time.asctime() + "\n"
            self.log += "Number of waiting time: " + str(count_wait) + "\n"
            self.log += str([x.poll() for x in self.process[i_group:]]) + "\n"
        self.log += "All sub programs are done.\n"

        # Writes the ended date.
        for j in range(len(self.program_list)):
            if end_time[j] == "":
                end_time[j] = time.asctime()

        # Checks process status.
        i_proc = copy.copy(i_group)
        for subproc in self.process[i_group:]:
            if subproc.poll() != None and subproc.wait() != 0:
                if not already_dead[i_proc]:
                    std_message = subproc.communicate()
                    warning_message = "\n\rWARNING: The program: \"" \
                        + self.program_list[i_proc].Command() \
                        + "\" does not work on the host '" \
                        + host[i_proc]  + "'.\n"\
                        + "status: " + str(subproc.wait()) \
                        + "\n\nOutput message:" \
                        + " \n  STDOUT: " + str(std_message[0]) \
                        + " \n  STDERR: " + str(std_message[1])
                    warning_message += "\n\rSee the file '" \
                        + self.output_file_list[i_proc].name \
                        + "' to read the standard output."
                    try:
                        self.output_file_list[i_proc].close()
                    except:
                        pass
                    self.log += warning_message
                    print warning_message
                    print "\n\rThe other sub-processus are still running...\n"
                    already_dead[i_proc] = True
            i_proc += 1

        # Tries to close all output files.
        if out_option == 'file':
            for outfile in self.output_file_list:
                try:
                    outfile.close()
                except:
                    pass

        # Writes the log.
        self.log += '-' * 78 + '\n'
        i_group = 0
        for i in range(len(self.program_list)):
            program = self.program_list[i]
            # New group ?
            if i > i_group and program.group != self.program_list[i-1].group:
                self.log += ("### GROUP " + str(program.group)
                             + " ###").center(78)
                self.log += "\n\n" + "-" * 78 + "\n\n"
                i_group = i
            self.log += program.Command()
            if self.log[-1] != "\n":
                self.log += "\n"
            self.log += "\nStatus: " + str(self.process[i].poll()) + "\n"
            self.log += "Hostname: " + str(host[i]) + "\n"
            self.log += "Started at " + str(beg_time[i]) + "\n"
            self.log += "Ended approximatively at " + str(end_time[i]) \
                        + "\n"
            self.log += "\n" + "-" * 78 + "\n\n"


    def RemoveTemporayFile(self):
        """Removes a few temporary files.
        Tries to remove the files in the attribute 'ouput_file_list' if the
        option 'out_option' was set to 'file' in the method 'RunNetwork'.
        """
        try:
            for f in self.output_file_list:
                os.remove(f.name)
        except:
            pass


    def Try(self):
        """Performs a dry run.
        """
        for program in self.program_list:
            program.Try()
            self.log += program.log
            if self.log[-1] != "\n":
                self.log += "\n"
            self.log += "\n" + "-" * 78 + "\n\n"
            if program.status != 0:
                raise Exception, "Program \"" + program.basename \
                      + "\" failed (status " + str(program.status) + ")."


###########
# PROGRAM #
###########


class Program:
    """This class manages a program associated with configuration files.
    """


    def __init__(self, name = None, config = None, format = " %a", group = 0):
        """Full initialization.

        \param name the program name.
        \param config the program configuration.
        \param format the format of arguments, where "%a" is replaced with
        the configuration files.
        \param group the group index.
        """
        import os

        if config is not None:
            ## \brief A configuration file.
            ## \details It can be the path (str) to the configuration file or a
            ## 'program_manager.Configuration' instance.
            self.config = config
        else:
            self.config = Configuration()

        ## The path of the program.
        self.name = name

        ## The basename of the program.
        self.basename = os.path.basename(name)

        ## A string.
        self.exec_path = "./"

        ## The format of arguments.
        self.format = format

        ## A string.
        self.priority = "0"

        ## None.
        self.output_directory = None

        ## The group index.
        self.group = group

        ## The status of the program.
        self.status = None

        ## A string.
        self.log = None


    def Run(self):
        """Executes the program.
        """
        self.config.Proceed()
        import commands
        self.status, self.log = commands.getstatusoutput(self.Command())


    def Command(self):
        """Returns the command to launch the program.
        The program must be ready to be launched.
        """
        if not self.IsReady():
            raise Exception, "Program \"" + self.name + "\" is not ready."
        format = self.format[:]
        command = "nice time " + self.name \
                  + format.replace("%a", self.config.GetArgument())
        return command


    def SetConfiguration(self, config, mode = "random", path = None,
                         replacement = None, additional_file_list = []):
        """Sets the program configuration files.
        \param config The configuration files associated with the program.
        \param mode The copy mode. Mode "raw" just copies to the target path,
        while mode "random" appends a random string at the end of the file
        name. Mode "random_path" appends a random directory in the path. This
        entry is useless if "config" is a Configuration instance.
        \param path The path where configuration files should be copied. If
        set to None, then the temporary directory "/tmp" is used. This entry
        is useless if "config" is a Configuration instance.
        \param replacement The map of replaced strings and the replacement
        values. This entry is useless if "config" is a Configuration
        instance.
        \param additional_file_list An additional configuration file or a
        list of additional configuration files to be managed. Just like
        primary configuration files, they are subject to the replacements and
        copies, but are not considered as program arguments.
        """
        if isinstance(config, list) or isinstance(config, str):
            if mode is None:
                mode = "tmp"
            self.config = Configuration(config, mode, path,
                                        additional_file_list)
            if replacement is not None:
                self.config.SetReplacementMap(replacement)
        else:
            self.config = config


    def Try(self):
        """Performs a dry run.
        """
        self.config.Proceed()
        import os
        if os.path.isfile(self.name):
            self.status = 0
        else:
            self.status = 1
        format = self.format[:]
        command = self.name + format.replace("%a", self.config.GetArgument())
        self.log = "Running program \"" + self.basename + "\":\n" \
                   + "   " + command


    def IsReady(self):
        """Checks whether the program can be launched.
        @return True if the program can be executed, False otherwise.
        """
        return self.config.IsReady()


#################
# CONFIGURATION #
#################


class Configuration:
    """This class manages configuration files.
    It proceeds replacements in the files and makes copies of the files.
    """


    def __init__(self, file_list = [], mode = "random", path = None,
                 additional_file_list = []):
        """Iniitialization of configuration information.
        \param file_list The configuration file or the list of configuration
        files to be managed.
        \param mode The copy mode. Mode "raw" just copies to the target path,
        while mode "random" appends a random string at the end of the file
        name. Mode "random_path" appends a random directory in the path.
        \param path The path where configuration files should be copied. If
        set to None, then the temporary directory "/tmp" is used.
        \param additional_file_list An additional configuration file or a
        list of additional configuration files to be managed. Just like
        primary configuration files, they are subject to the replacements and
        copies, but are not considered as program arguments.
        """
        import os
        if isinstance(file_list, str):
            ## The configuration file or list of configuration to be managed.
            self.raw_file_list = [file_list]
        else:
            self.raw_file_list = file_list

        ## The number of configuration files.
        self.Narg = len(self.raw_file_list)

        if isinstance(additional_file_list, str):
            self.raw_file_list.append(additional_file_list)
        else:
            self.raw_file_list += additional_file_list
        for f in self.raw_file_list:
            if not os.path.isfile(f):
                raise Exception, "Unable to find \"" + f + "\"."

        ## The list of replaced configuration files.
        self.file_list = []

        ## Are the configuration files ready to use?
        self.ready = False

        self.SetMode(mode)
        self.SetPath(path)

        ## The map of replaced strings and the replacement values.
        self.config = {}


    def SetMode(self, mode = "random"):
        """Sets the copy mode.
        \param mode The copy mode. Mode "raw" just copies to the target path,
        while mode "random" appends a random string at the end of the file
        name. Mode "random_path" appends a random directory in the path.
        """
        if mode not in ["random", "random_path", "raw"]:
            raise Exception, "Mode \"" + str(mode) + "\" is not supported."

        ## The copy mode.
        self.mode = mode


    def SetPath(self, path):
        """Sets the path.
        \param path The path where configuration fiels should be copied. If
        set to None, then the temporary directory "/tmp" is used.
        """
        if path is not None:
            ## The path where configuration files should be copied.
            self.path = path
        else:
            self.path = "/tmp/"


    def IsReady(self):
        """Tests whether the configuration files are ready for use.
        @return True if the configuration files are ready for use, False
        otherwise.
        """
        return self.ready or self.raw_file_list == []


    def GetReplacementMap(self):
        """Returns the map of replaced strings and the replacement values.
        @return The map of replaced strings and the replacement values.
        """
        return self.config


    def SetReplacementMap(self, config):
        """Sets the map of replaced strings and the replacement values.

        \param config the map of replaced strings and the replacement
        values.
        """
        self.config = config


    def SetConfiguration(self, config, mode = "random", path = None):
        """Initialization of configuration information, except file names.
        \param config The map of replaced strings and the replacement
        values.
        \param mode The copy mode. Mode "raw" just copies to the target path,
        while mode "random" appends a random string at the end of the file
        name. Mode "random_path" appends a random directory in the path.
        \param path The path where configuration fiels should be copied. If
        set to None, then the temporary directory "/tmp" is used.
        """
        self.SetMode(mode)
        self.SetPath(path)
        self.SetReplacementMap(config)
        self.Proceed()


    def Proceed(self):
        """Proceeds replacement in configuration files and copy them.
        """
        import os, shutil, fileinput
        self.file_list = []
        if self.mode == "random_path" and self.raw_file_list is not []:
            import tempfile
            random_path = tempfile.mkdtemp(prefix = self.path)
        for f in self.raw_file_list:
            if self.mode == "raw":
                if os.path.dirname(f) == self.path:
                    raise Exception, "Error: attempt to overwrite" \
                          + " the raw configuration file \"" + f + "\"."
                name = os.path.join(self.path, os.path.basename(f))
                shutil.copy(f, name)
            elif self.mode == "random":
                import tempfile
                name = os.path.join(self.path, os.path.basename(f))
                fd, name = tempfile.mkstemp(prefix = name + "-")
                shutil.copy(f, name)
            elif self.mode == "random_path":
                name = os.path.join(random_path, os.path.basename(f))
                shutil.copy(f, name)
            self.file_list.append(name)

        if self.file_list != []:
            for line in fileinput.input(self.file_list, 1):
                new_line = line
                for i in self.config.keys():
                    new_line = new_line.replace(str(i), str(self.config[i]))
                if self.mode == "random_path":
                    new_line = new_line.replace("%random_path%", random_path)
                print new_line,
            fileinput.close()
        self.ready = True


    def GetRawFileList(self):
        """Returns the list of reference (or raw) configuration files.
        @return The list of reference (or raw) configuration files.
        """
        return self.raw_file_list


    def SetRawFileList(self, file_list):
        """Sets the list of reference (or raw) configuration files.
        \param file_list The list of reference (or raw) configuration files.
        """
        self.raw_file_list = file_list
        self.ready = False


    def Clear(self):
        """Clears all, including configuration file names.
        """
        self.raw_file_list = []
        self.file_list = []
        self.ready = False
        self.mode = "random"
        self.path = "/tmp/"
        self.config = {}


    def GetArgument(self):
        """Returns the list of program arguments.
        @return The list of program arguments aggregated in a string (and
        split by an empty space).
        """
        if self.IsReady():
            return " ".join(self.file_list[:self.Narg])
        else:
            raise Exception, "Not ready."


if __name__ == "__main__":
    ## An instance 'program_manager.ProgramManager'.
    simulation = ProgramManager(Network())

    ## An instance 'program_manager.ProgramManager'.
    program = Program("/bin/echo", format = " Hello World!")
    simulation.AddProgram(program)

    simulation.Run()

    print simulation.log
