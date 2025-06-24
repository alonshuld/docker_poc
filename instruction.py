"""
Purpose: Instruction class
Author: Hanich 10
"""

from pydantic import BaseModel, field_validator

COMMANDS = ["CMD"]
COMMAND_INDEX = 0
INSTRUCTIONS_BEGINNING_INDEX = 1


class Instruction(BaseModel):
    """
    A BaseModel class of instruction
    Dockerfile is built from instructions
    """

    command: str
    arguments: list[str]

    @field_validator("command")
    @classmethod
    def command_validate(cls, value: str) -> str:
        """
        Checks if command is a valid field

        :param value: A command
        :raises ValidationError: When the command is not an available command
        :return: The command
        """
        if value.upper() not in COMMANDS:
            raise ValueError(f"{value} is not a valid command! available commands: {COMMANDS}")

        return value.upper()
