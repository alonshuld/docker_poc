"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

import gzip
from pathlib import Path
from typing import List, Tuple
from uuid import UUID
from datetime import datetime
from image import Image
from instruction import Instruction


HEADER = "*docker*image*file*"
DELIMITER = "delimiter"
DEPENDENCY_DELIMITER = "second_delimiter"
IMAGE_EXTENSION = ".dimg"
HEADER_FIELDS = 4
HEADER_INDEX = 0
INDEX_FILE_CREATION = 0
INDEX_LEN_INSTRUCTION = 1
INDEX_LEN_DEPENDENCY = 2


class ImageManager:
    """
    Handles all the images in the 
    """
    def __init__(self, images: List[Image]):
        self._images = images
    
    
    def get_image(self, id: UUID) -> Image:
        """
        Get specific image by id
 
        :param id: id of the wanted image
        :raises ValueError: No image with that id
        :return: The image with the id
        """
        for image in self._images:
            if image.id == id:

                return image
        
        raise ValueError("Invalid UUID")

    
    def _get_image_headers(self, image: Image) -> str:
        """
        Gives the header of the file that will represent the image
        HEADER _ creation date _ amount of instructions _ amount of files
        (Where _ = DELIMITER)

        :param image: The image
        :return: The header
        """
        header = HEADER
        header += DELIMITER
        header += str(image.creation_date)
        header += DELIMITER
        header += len(image.dockerfile.instructions)
        header += DELIMITER
        header += len(image.files)
        return header
    
    
    def _image_to_file(self, id: UUID) -> Tuple[str]:
        """
        Converts an image to file data
        Headers _ instruction 1 _ instruction 2 _ ... _ name1 * content1 _ name2 * content2 _ ...
        (Where _ = DELIMITER
               * = DEPENDENCY_DELIMITER)

        :param id: The id of the image
        :return: Name of file, the content of the file
        """
        image = self.get_image(id)
        file_data = self._get_image_headers(image)
        
        for instruction in image.dockerfile.instructions:   # write the instructions of the image
            file_data += DELIMITER
            file_data += " ".join([instruction.command] + instruction.arguments)
        
        for file in image.files:    # write the compressed dependencies files
            dependency_data = file.read()
            file_data += DELIMITER
            file_data += file.name
            file_data += DEPENDENCY_DELIMITER
            file_data += dependency_data
        
        return (image.name + IMAGE_EXTENSION, file_data)
    
    
    def _save_image(self, id: UUID, dir: str):
        """
        Saves the image to file named [image_name + IMAGE_EXTENSION] in the directory specified
        The image will be compressed with gzip

        :param id: The id of the image
        :param dir: The directory to save the image
        """
        file_name, file_data = self._image_to_file(id) 
        file_path = Path(dir) / file_name
        with open(file_path, "w") as image_file:
            image_file.write(gzip.compress(file_data))
    
    
    def delete_image(self, id: UUID):
        """
        Deletes an image from the manager

        :param id: The id of the image to remove
        :raises ValueError: No image with that id
        """
        image = self.get_image(id)
        self._images.remove(image)
    
    
    def _load_dependencies(self, dir: str, name: str, content: bytes):
        file_path = Path(dir) / name
        with open(file_path, "w+b") as dependency:
            dependency.write(content)
            dependency.seek(0)
        return dependency
            
    
    
    def _file_to_image(self, file_content: str, dir: str, file_name: str) -> Image:
        ERROR_MSG = f"Not {IMAGE_EXTENSION} format"
        
        file_fields = file_content.split(DELIMITER)
        
        if len(file_fields < HEADER_FIELDS):    # Check if file has at least the minimum amount of headers
            raise TypeError(ERROR_MSG)
        
        if file_fields[0] != HEADER:    # Checks if the first field is HEADER
            raise TypeError(ERROR_MSG)
        
        file_fields = file_fields[1:]   # trim HEADER
        
        try:    # Trying to cast the info fields of the file
            creation_date = datetime(file_fields[INDEX_FILE_CREATION])
            len_instruction = int(file_fields[INDEX_LEN_DEPENDENCY])
            len_dependency = int(file_fields[INDEX_LEN_INSTRUCTION])
        except Exception:
            raise TypeError(ERROR_MSG)
        
        # Checking if all the instructions and dependencies are available
        if len(file_fields) != len_instruction + len_dependency:
            raise TypeError(ERROR_MSG)
        
        image = Image()
        
        image.name = file_name.split(".")[0]
        image.creation_date = creation_date
        
        file_fields = file_fields[INDEX_LEN_INSTRUCTION + 1:]   # Trim the info fields
        
        instructions_data = file_fields[:len_instruction]
        dependencies_data = file_fields[len_instruction + 1: len_dependency]
        
        for instruction_data in instructions_data:  # adding instructions
            instructions_data = instructions_data.split()
            image.dockerfile.instructions.append(Instruction(command=instruction_data[0],
                                                             arguments=instruction_data[1:]))
        
        for dependency_data in dependencies_data:
            dependency = dependency_data.split(DEPENDENCY_DELIMITER)
            
            if len(dependency) != 2:
                raise TypeError(ERROR_MSG)

            name, content = dependency
            image.files.append(self._load_dependencies(dir, name, content))
        
        return image
    
    
    def load_image(self, image_path: str):
        with open(image_path, "r") as image_file:
            file_content = gzip.uncompress(image_file.read())
            self._images.append(self._file_to_image(file_content))