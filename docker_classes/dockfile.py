"""
Purpose: Dockerfile class that will contain the instructions for the image
Author: Hanich 10
"""

from pydantic import BaseModel

from instruction import COMMAND_INDEX, INSTRUCTIONS_BEGINNING_INDEX, Instruction

COMMENT = "#"
FIRST_CHAR_INDEX = 0


class Dockerfile(BaseModel):
    """
    Dockerfile class that holds a list of instructions for the image
    """

    instructions: list[Instruction] = []

    @classmethod
    def load_data(cls, data: str):
        """
        Load a Dockerfile data into a Dockerfile class

        :param data: Data of Dockerfile class
        :return: An instance of Dockerfile class loaded with the file
        """
        instructions: list[Instruction] = []
        lines = data.splitlines()
        for line in lines:
            if len(line) and line[FIRST_CHAR_INDEX] != COMMENT:
                line = line.split()
                instructions.append(
                    Instruction(command=line[COMMAND_INDEX], arguments=line[INSTRUCTIONS_BEGINNING_INDEX:])
                )
        return cls(instructions=instructions)

    def dump_data(self) -> str:
        """
        Dumps the data of the class to a string

        :return: a string that contains all the data of the current instance
        """
        data: list[str] = []
        for instruction in self.instructions:
            data.append(" ".join([instruction.command] + instruction.arguments))
        return "\n".join(data)
