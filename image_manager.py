"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

import gzip
import os
from typing import List, Tuple
from uuid import UUID
from datetime import datetime
from shutil import rmtree
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
FILE_FORMAT_ERROR = f"Not {IMAGE_EXTENSION} format"


class ImageManager:
    """
    Handles all the images in the 
    """
    def __init__(self, images: List[Image]):
        self._images = images
    
    
    def __exit__(self):
        """
        Removes all the dependencies of the images

        :raises OSError: Directory not found
        """
        for image in self._images:
            self._remove_image_dependencies(image)
    
    
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
        header += len(os.listdir(image.dependency_dir))
        return header
    
    
    def _image_to_file(self, id: UUID) -> Tuple[str, bytes]:
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
        
        for file_name in os.listdir(image.dependency_dir):    # write the compressed dependencies files
            file_path = os.path.join(image.dependency_dir, file_name)
            with open(file_path, "rb") as dependency_file:
                dependency_data = dependency_file.read()
                file_data += DELIMITER
                file_data += file_name
                file_data += DEPENDENCY_DELIMITER
                file_data += dependency_data
        
        return (image.name + IMAGE_EXTENSION, bytes(file_data))
    
    
    def _save_image(self, id: UUID, dir: str):
        """
        Saves the image to file named [image_name + IMAGE_EXTENSION] in the directory specified
        The image will be compressed with gzip

        :param id: The id of the image
        :param dir: The directory to save the image
        """
        file_name, file_data = self._image_to_file(id) 
        file_path = os.path.join(dir, file_name)
        with open(file_path, "wb") as image_file:
            image_file.write(gzip.compress(file_data))
    
    
    def _remove_image_dependency_dir(image: Image):
        """
        Removes the dependency directory of an image

        :param image: The image
        :raises OSError: No directory
        """
        try:
            rmtree(image.dependency_dir)
        except Exception:
            raise OSError(f"Couldn't remove {image.dependency_dir}")
    
    
    def delete_image(self, id: UUID):
        """
        Deletes an image from the manager

        :param id: The id of the image to remove
        :raises ValueError: No image with that id
        """
        image = self.get_image(id)
        self._remove_image_dependencies(image)
        self._images.remove(image)
    
    
    def _get_file_info(self, file_content: bytes) -> Tuple[datetime, List[str], List[bytes]]:
        """
        Trying to parses the file content and extracts the needed info from it

        :param file_content: The content of the docker image file
        :raises TypeError: File not in the right format
        :return: Tuple of the creation time, list of instructions and list of files
        """
        file_fields = file_content.decode().split(DELIMITER)
        
        if len(file_fields < HEADER_FIELDS):    # Check if file has at least the minimum amount of headers
            raise TypeError(FILE_FORMAT_ERROR)
        
        if file_fields[0] != HEADER:    # Checks if the first field is HEADER
            raise TypeError(FILE_FORMAT_ERROR)
        
        file_fields = file_fields[1:]   # trim HEADER
        
        # Trying to cast the info fields of the file
        try:
            creation_date = datetime(file_fields[INDEX_FILE_CREATION])
            len_instruction = int(file_fields[INDEX_LEN_DEPENDENCY])
            len_dependency = int(file_fields[INDEX_LEN_INSTRUCTION])
        except Exception:
            raise TypeError(FILE_FORMAT_ERROR)
        
        # Checking if all the instructions and dependencies are available
        if len(file_fields) != len_instruction + len_dependency:
            raise TypeError(FILE_FORMAT_ERROR)
        
        return (creation_date, file_fields[:len_instruction], bytes(file_fields[len_instruction + 1:]))
    
    
    def _load_dependency(self, dir: str, name: str, content: bytes):
        """
        Loads dependency into the directory

        :param dir: The directory of the dependency
        :param name: The name of the dependency
        :param content: The content of the dependency
        :return: File handle to the dependency *Opened!!!*
        """
        file_path = os.path.join(dir, name)
        with open(file_path, "wb") as dependency:
            dependency.write(content)
    
    
    def _file_to_image(self, file_content: bytes, dependency_dir: str, file_name: str) -> Image:
        """
        Loads the a file of an image into an image

        :param file_content: The content of the image file
        :param dependency_dir: The directory of the image dependency
        :param file_name: The name of the image file
        :raises TypeError: File not in right format
        :return: Instance of image with the data of the file
        """
        creation_date, instructions_data, dependencies_data = self._get_file_info(file_content)
        
        image = Image()
        
        image.name = file_name.split(IMAGE_EXTENSION)[0]
        image.creation_date = creation_date
        
        for instruction_data in instructions_data:  # Loading instructions
            instruction_data = instruction_data.split()
            image.dockerfile.instructions.append(Instruction(command=instruction_data[0],
                                                             arguments=instruction_data[1:]))
        
        for dependency_data in dependencies_data:   # Loading dependency files
            dependency_info = dependency_data.split(DEPENDENCY_DELIMITER)
            
            if len(dependency_info) != 2:    # Dependency must be [Name, Content]
                raise TypeError(FILE_FORMAT_ERROR)

            name, content = dependency_info
            self._load_dependency(dependency_dir, name, content)
        
        return image
    
    
    def load_image(self, image_path: str):
        """
        Load image from file

        :param image_path: The path of the image file
        """
        if IMAGE_EXTENSION not in image_path:
            raise ValueError(f"File doesn't contain the {IMAGE_EXTENSION} extension")
        with open(image_path, "rb") as image_file:
            file_content = gzip.decompress(image_file.read())
            self._images.append(self._file_to_image(file_content))
    
    
    def load_local_images(self, dir: str):
        """
        Loads all the images from the directory

        :param dir: The directory that contains the images
        """
        for file_name in os.listdir(dir):
            if IMAGE_EXTENSION in file_name:
                file_path = os.path.join(dir, file_name)
                self.load_image(file_path)
    
    
    def get_images(self) -> List[Image]:
        """
        Get all images from the image manager

        :return: The images
        """
        return self._images