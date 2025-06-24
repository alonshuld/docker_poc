"""
Purpose: Class that manages all the images
Author: Hanich 10
"""

import gzip
import os
from dataclasses import dataclass
from datetime import datetime
from shutil import rmtree
from uuid import UUID

from pydantic import BaseModel

from image import Image
from instruction import COMMAND_INDEX, INSTRUCTIONS_BEGINNING_INDEX, Instruction


class HeaderFields(BaseModel):
    """
    The fields that are in the header of the file
    """

    creation_date: datetime
    instructions_data: list[str]
    dependencies_data: list[bytes]


@dataclass(frozen=True)
class ImageFileFormat:
    """
    Holds the constant variables for format of the image
    """

    HEADER: str = "*&^dimg^&*"
    DELIMITER: str = "*&^&*"
    DEPENDENCY_DELIMITER: str = "*&^^&*"
    FILE_EXTENSION: str = ".dimg"
    INDEX_HEADER: int = 0
    INDEX_CREATION_DATE: int = 1
    INDEX_LEN_INSTRUCTIONS: int = 2
    INDEX_LEN_DEPENDENCIES: int = 3
    LEN_HEADER_FIELDS: int = 4
    DEFAULT_DOCKER_PATH: str = "/tmp/docker_poc/"
    DEFAULT_DEPENDENCIES_PATH: str = DEFAULT_DOCKER_PATH + "{image_name}/"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FORMAT_ERROR_MSG: str = "Not dimg format"
    LEN_DEPENDENCIES_FIELDS: int = 2


class ImageManager:
    """
    Handles all the images.
    Has a context manager that loads local file images on enter and deletes all the dependencies on exit
    * Creates images
    * Delete images and there dependencies
    * Save image to a file
    * Load images from files
    """

    def __init__(self, local_images_dir: str = ImageFileFormat.DEFAULT_DOCKER_PATH):
        self._local_images_dir = local_images_dir
        self._images: dict[UUID, Image] = {}

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
        if not dependency_dir:  # If no special dependency directory sets to default
            dependency_dir = ImageFileFormat.DEFAULT_DEPENDENCIES_PATH.format(image_name=image_name)

        image = Image(name=image_name, dependencies_dir=dependency_dir)
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

    def save_images_to_files(self, dir: str = ImageFileFormat.DEFAULT_DOCKER_PATH):
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
        if ImageFileFormat.FILE_EXTENSION not in image_path:
            raise ValueError(f"File doesn't contain the {ImageFileFormat.FILE_EXTENSION} extension")

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
            if ImageFileFormat.FILE_EXTENSION in file_name:
                file_path = os.path.join(dir, file_name)
                self.load_image(file_path)

    def get_images(self) -> list[Image]:
        """
        Get all images from the image manager

        :return: The images
        """
        return self._images.values()

    def _ls_dir(self, dir: str) -> list[str]:
        """
        Returns the result of ls in a directory
        If the directory doesn't exist return an empty list

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
        header = ImageFileFormat.HEADER
        header += ImageFileFormat.DELIMITER
        header += image.creation_date.strftime(ImageFileFormat.DATE_FORMAT)
        header += ImageFileFormat.DELIMITER
        header += str(len(image.dockerfile.instructions))
        header += ImageFileFormat.DELIMITER
        header += str(len(self._ls_dir(image.dependencies_dir)))
        return header

    def _image_to_file(self, image: Image) -> tuple[str, bytes]:
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
            file_data += ImageFileFormat.DELIMITER
            file_data += " ".join([instruction.command] + instruction.arguments)

        for file_name in self._ls_dir(image.dependencies_dir):  # write the compressed dependencies files if there is
            file_path = os.path.join(image.dependencies_dir, file_name)
            os.makedirs(image.dependencies_dir, exist_ok=True)
            with open(file_path, "rb") as dependency_file:
                dependency_data = dependency_file.read()
                file_data += ImageFileFormat.DELIMITER
                file_data += file_name
                file_data += ImageFileFormat.DEPENDENCY_DELIMITER
                file_data += dependency_data

        return (image.name + ImageFileFormat.FILE_EXTENSION, file_data.encode())

    def _save_image_to_file(self, image: Image, dir: str = ImageFileFormat.DEFAULT_DOCKER_PATH):
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
            rmtree(image.dependencies_dir)
        except FileNotFoundError:  # If image didn't had a dependency directory we pass
            pass

    def _file_header_to_info(self, file_content: bytes) -> HeaderFields:
        """
        Trying to parses the file content and extracts the needed info from it

        :param file_content: The content of the docker image file
        :raises ValueError: File not in the right format
        :return: creation time, list of instructions and list of files
        """
        file_fields = file_content.decode().split(ImageFileFormat.DELIMITER)

        if (
            len(file_fields) < ImageFileFormat.LEN_HEADER_FIELDS
        ):  # Check if file has at least the minimum amount of headers
            raise ValueError(ImageFileFormat.FORMAT_ERROR_MSG)

        if file_fields[ImageFileFormat.INDEX_HEADER] != ImageFileFormat.HEADER:  # Checks if the first field is HEADER
            raise ValueError(ImageFileFormat.FORMAT_ERROR_MSG)

        # Trying to cast the header fields of the file
        try:
            creation_date = datetime.strptime(
                file_fields[ImageFileFormat.INDEX_CREATION_DATE], ImageFileFormat.DATE_FORMAT
            )
            len_instruction = int(file_fields[ImageFileFormat.INDEX_LEN_INSTRUCTIONS])
            len_dependency = int(file_fields[ImageFileFormat.INDEX_LEN_DEPENDENCIES])
        except ValueError as e:
            e.add_note(ImageFileFormat.FORMAT_ERROR_MSG)
            raise e

        file_fields = file_fields[ImageFileFormat.LEN_HEADER_FIELDS :]  # Trim header fields

        # Checking if all the fields left are exactly the fields we expect
        if len(file_fields) != len_instruction + len_dependency:
            raise ValueError(ImageFileFormat.FORMAT_ERROR_MSG)

        header_fields = HeaderFields(
            creation_date=creation_date,
            instructions_data=file_fields[:len_instruction],
            dependencies_data=[dependency_data.encode() for dependency_data in file_fields[len_instruction:]],
        )

        return header_fields

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
        header_fields = self._file_header_to_info(file_content)
        image_name = file_name.split(ImageFileFormat.FILE_EXTENSION)[0]

        if not dependency_dir:  # If no special dependency directory sets to default
            dependency_dir = ImageFileFormat.DEFAULT_DEPENDENCIES_PATH.format(image_name=image_name)

        image = Image(name=image_name, creation_date=header_fields.creation_date, dependencies_dir=dependency_dir)

        for instruction_data in header_fields.instructions_data:  # Loading instructions
            instruction_data = instruction_data.split()
            image.dockerfile.instructions.append(
                Instruction(
                    command=instruction_data[COMMAND_INDEX], arguments=instruction_data[INSTRUCTIONS_BEGINNING_INDEX:]
                )
            )

        for dependency_data in header_fields.dependencies_data:  # Loading dependency files
            dependency_info = dependency_data.split(ImageFileFormat.DEPENDENCY_DELIMITER)

            if len(dependency_info) != ImageFileFormat.LEN_DEPENDENCIES_FIELDS:  # Dependency must be [Name, Content]
                raise TypeError(ImageFileFormat.FORMAT_ERROR_MSG)

            name, content = dependency_info
            self._load_dependency(dependency_dir, name, content)

        return image
