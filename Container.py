from enum import Enum
from uuid import UUID, uuid4
import sys
import subprocess
from image import Image
from ContainersErrors import ContainersErrors

class State(Enum):
    """ Container's State Enum """
    CREATED = 0
    RUNNING = 1
    EXITED = 2
    STOPPED = 3

class Container:
    """ Container class - execable instance of Docker image. """

    def __init__(self, name: str, image: Image, cpu_limit: float, memory_limit: float):
        # valid arguments
        if not is_percentage_number(cpu_limit):
            raise ValueError(ContainersErrors.CPU_LIMIT_VALUE_OUT_OF_SCOPE)
        if memory_limit < 0:
            raise ValueError(ContainersErrors.MEM_LIMIT_VALUE_OUT_OF_SCOPE)

        self._name = name
        self._image = image
        self.id = uuid4()
        self.state = State.Created
        self._cpu_limit = cpu_limit
        self._memory_limit = memory_limit

    def run(self) -> None:
        """ Run the container """
        try:
            # TO ADD: add cgroups for cpu and RAM control

            unshare_command = self._build_unshare()

            popen_kwargs = {}
            # TO ADD: detach mode (add raise ValueError if mode is not valid)
            
            # interactive mode
            popen_kwargs["stdin"] = sys.stdin
            popen_kwargs["stdout"] = sys.stdout
            popen_kwargs["stderr"] = sys.stderr

            # run process on isolated enviroment
            self.process = subprocess.Popen(unshare_command, **popen_kwargs)
            # TO DO: assign the process to cgroup to limit CPU and RAM

        except FileNotFoundError:
            # TO ADD: clean up cgroup
            raise FileNotFoundError(ContainersErrors.EXECUTABLE_COMMAND_NOT_FOUND)
        except (PermissionError, OSError, subprocess.SubprocessError) as error:
            # PermissionError: issues with file permissions (cgroup files)
            # OSError: general OS errors (like invalid path for files)
            # subprocess.SubprocessError: base for subprocess module errors (Popen cration might raise)
            
            if self.process and self.process.poll() is None:
                self.process.terminate()

            # TO ADD: clean up cgroup

            raise error.add_note(ContainersErrors.START_UP_CONTAINER_ERROR)

        self.state = State.Running


    def stop(self) -> None:
        """ Stop the container running"""
        self.state = State.Stopped
        # stop container process
        raise NotImplementedError("Stop Container will be implemented later")
    
    def _build_unshare(self) -> list[str]:
        """
        function build the unshare command for creating new isolated enviroment
        for the subprocess.Popen function
        :return: list of str which contain the unshare command
        """
        # define the isolated enviroment
        unshare_command = ["sudo", "unshare", 
                           "--pid", # isolate process id
                           "--mount", # isolate mount file sytem
                           "--uts", # isolate hostname
                           "--ipc", # isolate inter process comunication
                           "--fork", # fork a new process to the new isolated enviroment
                           "--chroot", f"/tmp/docker_poc/{str(self.id)}"] # isolate the file ststem (change root dir)
        inner_commands = [
            "mount -t proc proc /proc",
            "mount -t sysfs sys /sys",
            "mount --bind /dev /dev",
            "mount -t tmpfs tmp /tmp",
            f"hostname {self._name}"
        ]

        last_command_str = " ".join(["echo", "hello" ,"world"]) # change later to our commands
        inner_commands.append(last_command_str)

        full_shell_command = " && ".join(inner_commands)
        unshare_command.extend(["/bin/sh", "-c", full_shell_command])

        return unshare_command

def is_percentage_number(number):
    """ helper function that check if number between 0 and 100
    :param number: number to check if it is a percentage
    :return: True if number between 0 and 100, else False
    """
    return 0 <= number <= 100