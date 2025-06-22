#!/usr/bin/env python

from uuid import UUID, uuid4
from typing import Final

CONTAINER_ID_NOT_FOUND: Final = "Container id is not exist"
class ContainerManager:
    """ Container Manager class - handle all the containers """
    def __init__(self):
        self._containers = []
    
    def run_container(self, id: UUID) -> None:
        """ run the container with given id 
        :parameter id: id of container to run
        :raises ValueError: when container id is not exist
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                container.run()
                return None
        raise ValueError(CONTAINER_ID_NOT_FOUND)
    
    def stop_container(self, id: UUID) -> None:
        """ stop the container with given id 
        :parameter id: id of container to stop running
        :raises ValueError: when container id is not exist
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                container.stop()
                return None
        raise ValueError(CONTAINER_ID_NOT_FOUND)
    
    def delete_container(self, id: UUID) -> None:
        """ delete no running container from container manager 
        :param id: id of container to delete from manager
        :raises ValueError: when container id is not exist
        :raises ValueError: when container is running
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                if container.state == 0: # need to define running state (0 is placeholder for now)
                    raise ValueError("Container is running right now! if you want to delete, stop it first.")
                else:
                    self._containers.remove(container)
                    return None
        raise ValueError(CONTAINER_ID_NOT_FOUND)
    
    def create_container(self, name: str, image, cpu_limit: float, memory_limit: float):
        """ create new container in the containers list
        :param name: the given name for the container
        :param image: the image that container is made from
        :param cpu_limit: percentage that container can use from the total cpu
        :param memory_limit: percentage that container can use from the total RAM
        :return: none
        """
        # To create new container and append to containers list
        # raise exception if container couldn't be created
        pass

    def get_containers(self):
        """ get the containers in container manager
        :return: list of the containers
        """
        return self._containers
