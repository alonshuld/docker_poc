"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

import gzip
from pathlib import Path
from typing import List, Tuple
from uuid import UUID
from image import Image


HEADER = "*docker*image*file*"
DELIMITER = "delimiter"
IMAGE_EXTENSION = ".dimg"


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
        header += str(image.creation_date)
        header += DELIMITER
        header += len(image.dockerfile.instructions)
        header += DELIMITER
        header += len(image.files)
        return header
    
    
    def _image_to_file(self, id: UUID) -> Tuple[str]:
        """
        Converts an image to file data
        Headers _ instruction 1 _ instruction 2 _ ... _ file 1 _ file 2 _ ...
        (Where _ = DELIMITER)

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
            file_data += dependency_data
        
        return (image.name + IMAGE_EXTENSION, file_data)
    
    
    def _save_image(self, id: UUID, dir: Path):
        """
        Saves the image to file named [image_name + IMAGE_EXTENSION] in the directory specified
        The image will be compressed with gzip

        :param id: The id of the image
        :param dir: The directory to save the image
        """
        file_name, file_data = self._image_to_file(id) 
        file_path = dir / file_name
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