"""
Purpose: Dockerfile class that will contain the instructions for the image
Author: Hanich 10
"""


from typing import List
from instruction import Instruction


class Dockerfile:
    """
    Dockerfile class that holds a list of instructions for the image
    """  
    def __init__(self, file_path: str):
        self.instructions = self.parse_file(file_path)
    
    
    def parse_file(self, file_path: str) -> List[Instruction]:
        """
        Parses a Dockerfile into instructions

        :param file_path: path to the Dockerfile
        :return: list of all instructions in the Dockerfile
        """
        file_instructions = []
        with open(file_path, 'r') as dockerfile:
            lines = dockerfile.read().splitlines()
            for line in lines:
                instruction = line.split()
                if len(instruction) > 0:    # skips empty lines
                    file_instructions.append(Instruction(command=instruction[0], arguments=instruction[1:]))
            
            return file_instructions
