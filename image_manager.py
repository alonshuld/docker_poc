"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

import gzip
import os
from typing import List, Tuple, Dict
from uuid import UUID
from datetime import datetime
from shutil import rmtree
from image import Image
from instruction import Instruction


HEADER = "*&^dimg^&*"
DELIMITER = "*&^&*"
DEPENDENCY_DELIMITER = "*&^^&*"
IMAGE_EXTENSION = ".dimg"
HEADER_FIELDS = 4
INDEX_HEADER = 0
INDEX_FILE_CREATION = 0
INDEX_LEN_INSTRUCTION = 1
INDEX_LEN_DEPENDENCY = 2
FILE_FORMAT_ERROR = "Not dimg format"
DEFAULT_DOCKER_PATH = "/tmp/docker_poc/"
DEFAULT_DEPENDENCY_PATH = DEFAULT_DOCKER_PATH + "{image_name}/"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ImageManager:
    """
    Handles all the images in the
    """

    def __init__(self, dir: str):
        self._local_images_dir = dir
        self._images: Dict[UUID, Image] = {}

    def __enter__(self):
        self.load_local_images(self._local_images_dir)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Removes all the dependencies of the images

        :raises OSError: Directory not found
        """
        for image in self._images.values():
            self._delete_image_dependency_dir(image)

    def build_image(self, image_name: str, dockerfile_path: str, dependency_dir: str = None):
        """
        Builds a new image
        To build a new image all its dependencies should already exist in DEFAULT_DEPENDENCY_DIR

        :param name: The name of the image
        :param dockerfile_path: The path to the Dockerfile
        :param dependency_dir: The directory of all the dependencies, defaults to DEFAULT_DOCKER_PATH + name
        """
        if dependency_dir == None:  # If no special dependency directory sets to default
            dependency_dir = DEFAULT_DEPENDENCY_PATH.format(image_name=image_name)

        image = Image(name=image_name, dependency_dir=dependency_dir)
        image.dockerfile.parse_file(dockerfile_path)
        self._images[image.id] = image

    def get_image(self, id: UUID) -> Image:
        """
        Get specific image by id

        :param id: id of the wanted image
        :raises ValueError: No image with that id
        :return: The image with the id
        """
        return self._images[id]

    def save_images_to_files(self, dir: str = DEFAULT_DOCKER_PATH):
        """
        Saves all images

        :param dir: The directory to save the images, defaults to DEFAULT_DOCKER_PATH
        """
        for image in self._images.values():
            self._save_image_to_file(image, dir)

    def delete_image(self, id: UUID):
        """
        Deletes an image from the manager

        :param id: The id of the image to remove
        :raises ValueError: No image with that id
        """
        image = self.get_image(id)
        self._delete_image_dependency_dir(image)
        self._images.remove(image)

    def load_image(self, image_path: str):
        """
        Load image from file

        :param image_path: The path of the image file
        """
        if IMAGE_EXTENSION not in image_path:
            raise ValueError(f"File doesn't contain the {IMAGE_EXTENSION} extension")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, "rb") as image_file:
            file_content = gzip.decompress(image_file.read())
            image = self._file_content_to_image(file_content, os.path.basename(image_path))
            self._images[image.id] = image

    def load_local_images(self, dir: str):
        """
        Loads all the images from the directory

        :param dir: The directory that contains the images
        """
        for file_name in self._ls_dir(dir):
            if IMAGE_EXTENSION in file_name:
                file_path = os.path.join(dir, file_name)
                self.load_image(file_path)

    def get_images(self) -> List[Image]:
        """
        Get all images from the image manager

        :return: The images
        """
        return self._images

    def _ls_dir(self, dir: str) -> List[str]:
        """
        Returns the result of ls in a dir

        :param dir: The dir
        :return: The files in it
        """
        try:
            return os.listdir(dir)
        except FileNotFoundError:
            return []

    def _image_to_file_header(self, image: Image) -> str:
        """
        Gives the header of the file that will represent the image
        HEADER _ creation date _ amount of instructions _ amount of files
        (Where _ = DELIMITER)

        :param image: The image
        :return: The header
        """
        header = HEADER
        header += DELIMITER
        header += image.creation_date.strftime(DATE_FORMAT)
        header += DELIMITER
        header += str(len(image.dockerfile.instructions))
        header += DELIMITER
        header += str(len(self._ls_dir(image.dependency_dir)))
        return header

    def _image_to_file(self, image: Image) -> Tuple[str, bytes]:
        """
        Converts an image to file data
        Headers _ instruction 1 _ instruction 2 _ ... _ name1 * content1 _ name2 * content2 _ ...
        (Where _ = DELIMITER
               * = DEPENDENCY_DELIMITER)

        :param Image: The image
        :return: Name of file and the content of the file
        """
        file_data = self._image_to_file_header(image)

        for instruction in image.dockerfile.instructions:  # write the instructions of the image
            file_data += DELIMITER
            file_data += " ".join([instruction.command] + instruction.arguments)

        for file_name in self._ls_dir(image.dependency_dir):  # write the compressed dependencies files
            file_path = os.path.join(image.dependency_dir, file_name)
            os.makedirs(image.dependency_dir, exist_ok=True)
            with open(file_path, "rb") as dependency_file:
                dependency_data = dependency_file.read()
                file_data += DELIMITER
                file_data += file_name
                file_data += DEPENDENCY_DELIMITER
                file_data += dependency_data

        return (image.name + IMAGE_EXTENSION, file_data.encode())

    def _save_image_to_file(self, image: Image, dir: str = DEFAULT_DOCKER_PATH):
        """
        Saves the image to file named [image_name + IMAGE_EXTENSION] in the directory specified
        The image will be compressed with gzip

        :param image: The image
        :param dir: The directory to save the image, defaults to DEFAULT_DOCKER_PATH
        """
        file_name, file_data = self._image_to_file(image)
        file_path = os.path.join(dir, file_name)
        os.makedirs(dir, exist_ok=True)
        with open(file_path, "wb") as image_file:
            image_file.write(gzip.compress(file_data))

    def _delete_image_dependency_dir(self, image: Image):
        """
        Removes the dependency directory of an image

        :param image: The image
        :raises OSError: No directory
        """
        try:
            rmtree(image.dependency_dir)
        except FileNotFoundError:  # If image didn't had a dependency directory we pass
            pass

    def _file_header_to_info(self, file_content: bytes) -> Tuple[datetime, List[str], List[bytes]]:
        """
        Trying to parses the file content and extracts the needed info from it

        :param file_content: The content of the docker image file
        :raises ValueError: File not in the right format
        :return: Tuple of the creation time, list of instructions and list of files
        """
        file_fields = file_content.decode().split(DELIMITER)

        if len(file_fields) < HEADER_FIELDS:  # Check if file has at least the minimum amount of headers
            raise ValueError(FILE_FORMAT_ERROR)

        if file_fields[0] != HEADER:  # Checks if the first field is HEADER
            raise ValueError(FILE_FORMAT_ERROR)

        file_fields = file_fields[INDEX_HEADER + 1 :]  # trim HEADER

        # Trying to cast the header fields of the file
        try:
            creation_date = datetime.strptime(file_fields[INDEX_FILE_CREATION], DATE_FORMAT)
            len_instruction = int(file_fields[INDEX_LEN_INSTRUCTION])
            len_dependency = int(file_fields[INDEX_LEN_DEPENDENCY])
        except ValueError as e:
            e.add_note(FILE_FORMAT_ERROR)
            raise e

        file_fields = file_fields[INDEX_LEN_DEPENDENCY + 1 :]  # Trim header fields

        # Checking if all the fields left are exactly the fields we expect
        if len(file_fields) != len_instruction + len_dependency:
            raise ValueError(FILE_FORMAT_ERROR)

        return (creation_date, file_fields[:len_instruction], bytes(file_fields[len_instruction + 1 :]))

    def _load_dependency(self, dir: str, name: str, content: bytes):
        """
        Loads dependency into the directory

        :param dir: The directory of the dependency
        :param name: The name of the dependency
        :param content: The content of the dependency
        :return: File handle to the dependency *Opened!!!*
        """
        file_path = os.path.join(dir, name)
        os.makedirs(dir, exist_ok=True)
        with open(file_path, "wb") as dependency:
            dependency.write(content)

    def _file_content_to_image(self, file_content: bytes, file_name: str, dependency_dir: str = None) -> Image:
        """
        Loads the a file of an image into an image

        :param file_content: The content of the image file
        :param dependency_dir: The directory of the image dependency, defaults to DEFAULT_DOCKER_DIR + name
        :param file_name: The name of the image file
        :raises TypeError: File not in right format
        :return: Instance of image with the data of the file
        """
        creation_date, instructions_data, dependencies_data = self._file_header_to_info(file_content)
        image_name = file_name.split(IMAGE_EXTENSION)[0]

        if dependency_dir == None:  # Default dir
            dependency_dir = DEFAULT_DEPENDENCY_PATH.format(image_name=image_name)

        image = Image(name=image_name, creation_date=creation_date, dependency_dir=dependency_dir)

        for instruction_data in instructions_data:  # Loading instructions
            instruction_data = instruction_data.split()
            image.dockerfile.instructions.append(
                Instruction(command=instruction_data[0], arguments=instruction_data[1:])
            )

        for dependency_data in dependencies_data:  # Loading dependency files
            dependency_info = dependency_data.split(DEPENDENCY_DELIMITER)

            if len(dependency_info) != 2:  # Dependency must be [Name, Content]
                raise TypeError(FILE_FORMAT_ERROR)

            name, content = dependency_info
            self._load_dependency(dependency_dir, name, content)

        return image
