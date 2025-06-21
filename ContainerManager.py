#!/usr/bin/env python

from uuid import UUID, uuid4

class ContainerManager:
    """ Container Manager class - handle all the containers """
    def __init__(self):
        self._containers = []
    
    def run_container(self, id: UUID):
        """ run the container with given id 
        :parameter id: id of container to run
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                container.run()
        # what happens if id is not found? (exception or return bool)
    
    def stop_container(self, id: UUID):
        """ stop the container with given id 
        :parameter id: id of container to stop running
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                container.stop()
        # what happens if id is not found? (exception or return bool)
    
    def delete_container(self, id: UUID):
        """ delete no running container from container manager 
        :param id: id of container to delete from manager
        :return: none
        """
        for container in self._containers:
            if container.id == id:
                if container.state == 0: # need to define running state (0 is placeholder for now)
                    # what happens if container running? (exception or return bool)
                    # who prints the error details (the container manager of docker manager of something else)?
                    pass
                else:
                    self._containers.remove(container)
        # what happens if id is not found? (exception or return bool)
    
    def create_container(self, name: str, image, cpu_limit: float, memory_limit: float):
        """ create new container in the containers list
        :param name: the given name for the container
        :param image: the image that container is made from
        :param cpu_limit: percentage that container can use from the total cpu
        :param memory_limit: percentage that container can use from the total RAM
        :return: none
        """
        # To create new container and append to containers list
        # what happens if container couldn't be created? (exception or return bool)
        pass

    def get_containers(self):
        """ get the containers in container manager
        :return: list of the containers
        """
        return self._containers
