"""
Purpose: Instruction class
Author: Hanich 10
"""


from pydantic import BaseModel, field_validator, ValidationError
from typing import List


COMMANDS = [
    "CMD"
]


class Instruction(BaseModel):
    """
    A BaseModel class of instruction
    Dockerfile is built from instructions
    """
    command: str
    arguments: List[str]
    
    @field_validator('command')
    @classmethod
    def command_validate(cls, value: str) -> str:
        """
        Checks if command is a valid field

        :param value: A command
        :raises ValidationError: When the command is not an available command
        :return: The command 
        """
        if value not in COMMANDS:
            raise ValueError(f"{value} is not a valid command!")
        
        return value
