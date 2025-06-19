"""
Purpose: Class that manages all the images
Author: Hanich 10
"""


from pathlib import Path
from typing import List
from uuid import UUID
from image import Image


HEADER = b"*docker*image*file*"


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
        :raises ValueError: if there is no image with that id
        :return: the image with the id
        """
        for image in self._images:
            if image.id == id:

                return image
        
        raise ValueError("Invalid UUID")
    
    
    def _save_image(self, id: UUID, dir: Path):
        image = self.get_image(id)
        file_path = dir / (image.name + ".img")
        with open(file_path, "wb") as image_file:
            pass    # TODO: Start right the file in the right format