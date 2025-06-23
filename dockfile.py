"""
Purpose: Dockerfile class that will contain the instructions for the image
Author: Hanich 10
"""

from pydantic import BaseModel
from typing import List
from instruction import Instruction


COMMENT = "#"


class Dockerfile(BaseModel):
    """
    Dockerfile class that holds a list of instructions for the image
    """

    instructions: List[str] = []

    def parse_file(self, file_path: str):
        """
        Parses a Dockerfile into instructions

        :param file_path: path to the Dockerfile
        :return: list of all instructions in the Dockerfile
        """
        self.instructions = []
        with open(file_path, "r") as dockerfile:
            lines = dockerfile.read().splitlines()
            for instruction in (line.split(" ") for line in lines if line and line[0] != COMMENT):
                self.instructions.append(Instruction(command=instruction[0], arguments=instruction[1:]))
