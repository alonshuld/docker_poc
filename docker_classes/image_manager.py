"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

from uuid import UUID

from .dockfile import Dockerfile
from .image import DOCKER_DIR, FILE_EXTENSION, IMAGE_DEPENDENCIES_DIR, Image, ls_files


class ImageManager:
    """
    Handles all the images.
    Has a context manager that loads local file images on enter and deletes all the dependencies on exit
    * Creates images
    * Delete images and there dependencies
    * Save image to a file
    * Load images from files
    """

    def __init__(self):
        self._images: dict[UUID, Image] = {}

    def __enter__(self):
        self.load_local_images()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Removes all the dependencies of the images

        :raises OSError: Directory not found
        """
        for image in self._images.values():
            del image

    def build_image(self, image_name: str, dockerfile_path: str):
        """
        Builds a new image
        To build a new image all its dependencies should already exist in DEFAULT_DEPENDENCY_DIR

        :param name: The name of the image
        :param dockerfile_path: The path to the Dockerfile
        :param dependency_dir: The directory of all the dependencies, defaults to DEFAULT_DOCKER_PATH + name
        """
        with open(dockerfile_path, "r") as dockerfile:
            dockerfile_data = dockerfile.read()
        image = Image(
            name=image_name,
            dependencies_dir=IMAGE_DEPENDENCIES_DIR.format(image_name=image_name, dependency_name=""),
            dockerfile=Dockerfile.load_data(dockerfile_data),
        )
        self._images[image.id] = image

    def get_image(self, id: UUID) -> Image:
        """
        Get specific image by id

        :param id: id of the wanted image
        :raises ValueError: No image with that id
        :return: The image with the id
        """
        return self._images[id]

    def save_images_to_files(self):
        """
        Saves all images

        :param dir: The directory to save the images, defaults to DEFAULT_DOCKER_PATH
        """
        for image in self._images.values():
            image.dump_file()

    def delete_image(self, id: UUID):
        """
        Deletes an image from the manager

        :param id: The id of the image to remove
        :raises ValueError: No image with that id
        """
        del self._images[id]

    def load_image(self, image_path: str):
        """
        Load image from file

        :param image_path: The path of the image file
        """
        if FILE_EXTENSION not in image_path:
            raise ValueError("Image file must contain '.dimg' extension")

        new_image = Image.load_file(image_path)
        self._images[new_image.id] = new_image

    def load_local_images(self):
        """
        Loads all the images from the directory

        :param dir: The directory that contains the images
        """
        for path in ls_files(DOCKER_DIR):
            self.load_image(path)

    def get_images(self) -> list[Image]:
        """
        Get all images from the image manager

        :return: The images
        """
        return self._images.values()
