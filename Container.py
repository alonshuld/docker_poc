from enum import Enum
from uuid import UUID, uuid4
import sys
import subprocess
import os
import time
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
        self._process = None # in run function store the container's process
        self._pid = 0 # in run function change to container process's pid

    def run(self) -> None:
        """ Run the container """
        try:
            # TO ADD: add cgroups for cpu and RAM control

            unshare_command = self._build_enviroment()

            popen_kwargs = {}
            # TO ADD: detach mode (add raise ValueError if mode is not valid)
            
            # interactive mode
            popen_kwargs["stdin"] = sys.stdin
            popen_kwargs["stdout"] = sys.stdout
            popen_kwargs["stderr"] = sys.stderr

            # run process on isolated enviroment
            self._process = subprocess.Popen(unshare_command, **popen_kwargs)
            self._pid = self._process.pid
            # TO DO: assign the process to cgroup to limit CPU and RAM

        except FileNotFoundError:
            # TO ADD: clean up cgroup
            raise FileNotFoundError(ContainersErrors.EXECUTABLE_COMMAND_NOT_FOUND)
        except (PermissionError, OSError, subprocess.SubprocessError) as error:
            # PermissionError: issues with file permissions (cgroup files)
            # OSError: general OS errors (like invalid path for files)
            # subprocess.SubprocessError: base for subprocess module errors (Popen cration might raise)
            
            if self._process and self._process.poll() is None:
                self._process.terminate()

            # TO ADD: clean up cgroup

            raise error.add_note(ContainersErrors.START_UP_CONTAINER_ERROR)

        self.state = State.Running


    def stop(self) -> None:
        """ Stop the container running and terminate the container's process """

        # check if container was run by the current Docker script
        if self._process and self._process.poll() is None:
            # try to gracefully close the process
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # if cannot close the process gracefully, kill it
                self._process.kill()
        else:
            # container was run by previous Docker script
            # popen handler not exist any more, use pid instead

            # check if container's process is exist and you can signal it
            try:
                os.kill(self._pid, 0)
            except ProcessLookupError:
                # TO ADD: clean up cgroup
                raise ProcessLookupError(ContainersErrors.CONTAINER_PROCESS_NOT_FOUND)
            except PermissionError:
                raise PermissionError(ContainersErrors.PERMISSION_DENIED_KILL_PROCESS)
            
            # try gracefully terminate container's process
            try:
                subprocess.run(["sudo", "kill", str(self._pid)], check=True)
            except subprocess.CalledProcessError:
                # TO ADD: clean up cgroup
                raise subprocess.CalledProcessError(ContainersErrors.FAIL_SIGTERM)
            
            try:
                self._wait()
            except TimeoutError:
                # process didn't exit gracefully - send SIGKILL
                try:
                    subprocess.run(["sudo", "kill", "-9", str(self._pid)], check=True)
                except subprocess.CalledProcessError:
                    raise subprocess.CalledProcessError(ContainersErrors.FAIL_SIGKILL)

        # TO ADD: clean up cgroup

        self.state = State.Stopped
    
    def _build_enviroment(self) -> list[str]:
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
    
    def _wait(self, timeout_seconds=5) -> None:
        """ function wait container's process to exit, if timeout is reached raise Timeout
        :param timeout_seconds: time to wait for gracefull closing
        :raises PermissionError: if script doesn't have permissions to signal process
        :raise TimeoutError: if process does not exit in the timeout frame
        :return: None
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                os.kill(self._pid, 0)
                time.sleep(0.1)
            except ProcessLookupError:
                # process exited gracefully and no longer exists
                return None
            except PermissionError:
                # may happen if permissions chaged since the last check
                raise PermissionError(ContainersErrors.PERMISSION_DENIED_KILL_PROCESS)
        raise TimeoutError(ContainersErrors.TIME_OUT_WAITING)


def is_percentage_number(number):
    """ helper function that check if number between 0 and 100
    :param number: number to check if it is a percentage
    :return: True if number between 0 and 100, else False
    """
    return 0 <= number <= 100
