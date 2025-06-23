from enum import Enum

class ContainersErrors(Enum):
    """ Errors messages for Containers """
    CONTAINER_ID_NOT_FOUND = "Container id is not exist"
    TRYING_TO_STOP_A_RUNNING_CONTAINER = "Container is running right now! if you want to delete, stop it first."
    CPU_LIMIT_VALUE_OUT_OF_SCOPE = "CPU limit should be a precentage number between 0 and 100 (from the total CPU)"
    MEM_LIMIT_VALUE_OUT_OF_SCOPE = "RAM memory limit should be a positive number (scale units in MB)"
