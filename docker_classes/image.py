"""
Purpose: Image class that will contain all needed information
Author: Hanich 10
"""

import datetime
import gzip
import json
import os
from shutil import rmtree
from typing import Final, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .dockfile import Dockerfile

DOCKER_DIR: Final = "/tmp/docker_poc/"
FILE_EXTENSION: Final = ".dimg"
IMAGE_PATH: Final = DOCKER_DIR + "{image_name}" + FILE_EXTENSION
IMAGE_DEPENDENCIES_DIR: Final = DOCKER_DIR + "{image_name}/{dependency_name}"
DATE_FORMAT: Final = "%Y-%m-%d %H:%M:%S"

NAME_KEY: Final = "name"
DOCKERFILE_KEY: Final = "dockerfile"
DATA_KEY: Final = "data"
DEPENDENCIES_KEY: Final = "dependencies"
CREATION_DATE_KEY: Final = "creation_date"


def ls_files(dir: str) -> list[str]:
    """
    Returns the path of all the files in a directory
    If the directory doesn't exist return an empty list

    :param dir: The dir
    :return: The files in it
    """
    try:
        return [path for path in os.listdir(dir) if os.path.isfile(path)]
    except FileNotFoundError:
        return []


class Image(BaseModel):
    """
    Holds all information that image needs
    """

    name: str
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now().replace(microsecond=0))
    dependencies_dir: str
    dockerfile: Dockerfile = Field(default_factory=Dockerfile)

    def dump_file(self):
        """
        Dumps the image into a file.
        The file will be in a 'json' format and will be zipped with 'gzip'
        """
        image_data = {}
        image_data[NAME_KEY] = self.name
        image_data[CREATION_DATE_KEY] = self.creation_date.strftime(DATE_FORMAT)

        # Dump Dockerfile to data
        image_data[DOCKERFILE_KEY] = self.dockerfile.dump_data()

        # Dump dependencies to data
        image_data[DEPENDENCIES_KEY] = []
        dependencies_path = IMAGE_DEPENDENCIES_DIR.format(image_name=self.name, dependency_name="")
        os.makedirs(dependencies_path, exist_ok=True)
        for dependency_path in ls_files(dependencies_path):
            with open(dependency_path, "rb") as dependency_file:
                image_data[DEPENDENCIES_KEY].append(
                    {NAME_KEY: os.path.basename(dependency_path), DATA_KEY: dependency_file.read()}
                )

        # Compress data
        compressed_data = gzip.compress(json.dumps(image_data).encode())

        # Save data to file
        with open(IMAGE_PATH.format(image_name=self.name), "wb") as image_file:
            image_file.write(compressed_data)

    @classmethod
    def load_file(cls, file_path: str) -> Self:
        """
        Loads an Image file into an Image class

        :param file_path: Path to an Image file
        :return: Image instance loaded with the data of the Image file
        """
        # Load data from file
        with open(file_path, "rb") as file:
            compressed_data = file.read()

        # Decompress data
        image_data = json.loads(gzip.decompress(compressed_data).decode())

        # Load dependencies
        dependencies_dir = IMAGE_DEPENDENCIES_DIR.format(image_name=image_data[NAME_KEY], dependency_name="")
        os.makedirs(dependencies_dir, exist_ok=True)
        for dependency_data in image_data[DEPENDENCIES_KEY]:
            with open(
                IMAGE_DEPENDENCIES_DIR.format(
                    image_name=image_data[NAME_KEY], dependency_name=dependency_data[NAME_KEY]
                ),
                "wb",
            ) as dependency_file:
                dependency_file.write(dependency_data[DATA_KEY])

        # Load Dockerfile
        dockerfile = Dockerfile.load_data(image_data[DOCKERFILE_KEY])

        return cls(
            name=image_data[NAME_KEY],
            creation_date=datetime.datetime.strptime(image_data[CREATION_DATE_KEY], DATE_FORMAT),
            dependencies_dir=dependencies_dir,
            dockerfile=dockerfile,
        )

    def __del__(self):
        """
        Removes the dependencies of an image if possible
        """
        try:
            rmtree(self.dependencies_dir)
        except FileNotFoundError:
            pass
