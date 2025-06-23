"""
Purpose: Dockerfile class that will contain the instructions for the image
Author: Hanich 10
"""


from typing import List
from instruction import Instruction


COMMENT = "#"


class Dockerfile:
    """
    Dockerfile class that holds a list of instructions for the image
    """  
    def __init__(self, file_path: str = ""):
        if file_path == "":
            self.instructions = []
        else:
            self.instructions = self.parse_file(file_path)
    
    
    def parse_file(self, file_path: str):
        """
        Parses a Dockerfile into instructions

        :param file_path: path to the Dockerfile
        :return: list of all instructions in the Dockerfile
        """
        file_instructions = []
        with open(file_path, 'r') as dockerfile:
            lines = dockerfile.read().splitlines()
            for line in lines:
                if line != "" and line[0] != COMMENT:   # Doesn't read commented and empty lines
                    instruction = line.split(" ")
                    file_instructions.append(Instruction(command=instruction[0], arguments=instruction[1:]))
            
            self.instructions = file_instructions
