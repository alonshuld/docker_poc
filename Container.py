from enum import Enum
from uuid import UUID, uuid4
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
        self.state = State.Running
        # run container
        raise NotImplementedError("Run Container will be implemented later")

    def stop(self) -> None:
        """ Stop the container running"""
        self.state = State.Stopped
        # stop container process
        raise NotImplementedError("Stop Container will be implemented later")

def is_percentage_number(number):
    """ helper function that check if number between 0 and 100
    :param number: number to check if it is a percentage
    :return: True if number between 0 and 100, else False
    """
    return 0 <= number <= 100
