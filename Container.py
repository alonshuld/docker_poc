#!/usr/bin/env python

from enum import Enum
from uuid import UUID, uuid4

class State(Enum):
    """ Container's State Enum """
    Created = 0
    Running = 1
    Exited = 2
    Stopped = 3

class Container:
    """ Container class """

    def __init__(self, name: str, image, cpu_limit: float, memory_limit: float):
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

    def stop(self) -> None:
        """ Stop the container running"""
        self.state = State.Stopped
        # stop container process
