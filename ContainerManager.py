from uuid import UUID
from typing import Final, dict
from Container import State, Container
from image import Image
from ContainersErrors import ContainersErrors, RunningContainerException

class ContainerManager:
    """ Container Manager class - store and manage all the containers objects in program"""

    def __init__(self):
        self._containers: dict[UUID, Container] = {}
    
    def run_container(self, id: UUID) -> None:
        """ run the container with given id
        :parameter id: id of container to run.
        :raises ValueError: when container id does not exist.
        :return: none
        """
        if id not in self._containers.keys():
            raise ValueError(ContainersErrors.CONTAINER_ID_NOT_FOUND)
        self._containers[id].run()
        
    
    def stop_container(self, id: UUID) -> None:
        """ stop the container with given id 
        :parameter id: id of container to stop running.
        :raises ValueError: when container id does not exist.
        :return: none
        """
        if id not in self._containers.keys():
            raise ValueError(ContainersErrors.CONTAINER_ID_NOT_FOUND)
        self._containers[id].stop()
    
    def delete_container(self, id: UUID) -> None:
        """ delete no running container from container manager 
        :param id: id of container to delete from manager.
        :raises ValueError: when container id does not exist.
        :raises ValueError: when container is running.
        :return: none
        """
        if id not in self._containers.keys():
            raise ValueError(ContainersErrors.CONTAINER_ID_NOT_FOUND)
        if self._containers[id].state == State.RUNNING:
            raise RunningContainerException(ContainersErrors.TRYING_TO_STOP_A_RUNNING_CONTAINER)
        self._containers.pop(id)
    
    def create_container(self, name: str, image: Image, cpu_limit: float, memory_limit: float) -> None:
        """ create new container in the containers dict
        :param name: the given name for the container.
        :param image: the image that container is made from.
        :param cpu_limit: percentage that container can use from the total cpu.
        :param memory_limit: percentage that container can use from the total RAM.
        :return: none
        """
        new_container = Container(name, image, cpu_limit, memory_limit)
        self._containers[new_container.id] = new_container

    def get_containers(self) -> dict[Container]:
        """ get the containers in container manager
        :return: dict of the id as key and container as value 
        """
        return self._containers
