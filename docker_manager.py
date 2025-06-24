from typing import Final

from tabulate import tabulate

from container_manager import ContainerManager
from image_manager import ImageManager

# Finals
EXIT_COMMAND: Final = "exit"
HELP_COMMAND: Final = "help"
BUILD_COMMAND: Final = "build"
IMAGES_COMMAND: Final = "images"
COMMAND_PREFIX: Final = "docker"
COMMAND_INDEX: Final = 1

AVAILABLE_COMMANDS = {
    EXIT_COMMAND: "Exit the program",
    HELP_COMMAND: "Get help",
    BUILD_COMMAND: "Build an image from DockerFile.",
    "run": "Creates and starts a new container from an image.",
    "ps": "list all the existing containers.",
    IMAGES_COMMAND: "Lists all existing images.",
    "stop": "Stops a running container.",
    "rm": "Removes a stopped container.",
    "rmi": "Removes an image.",
}


class DockerManager:
    """The main Docker Manager - Docker Client"""

    def __init__(self, image_manager: ImageManager, container_manager: ContainerManager):
        self._image_manager = image_manager
        self._container_manager = container_manager

    def get_input(self) -> list[str]:
        """function get the input from user
        :return: the user's input as list of words
        """
        user_input = []
        while len(user_input) == 0:
            user_input = input("\n----$: ").split()
        return user_input

    def interpret_command(self, user_input: list[str]) -> bool:
        """function interpret the input and call to the suitable handle function
        :param input: list of the words in user's input line
        :return: False if user want to exit, else True
        """
        if user_input[0].lower() == EXIT_COMMAND:
            return False

        if user_input[0].lower() == HELP_COMMAND:
            self.give_help()
            return True

        if user_input[0].lower() != COMMAND_PREFIX:
            print("commands which not 'exit' or 'help' must start with '", COMMAND_PREFIX, "' prefix")
            return True

        if len(user_input) > 1 and user_input[COMMAND_INDEX] not in AVAILABLE_COMMANDS.keys():
            print("command", user_input[COMMAND_INDEX], "is unknown")
            return True

        if user_input[COMMAND_INDEX] == "images":
            self.print_images()
            return True
        
        if user_input[COMMAND_INDEX] == "build":
            image_name = input("Enter the image name: ")
            image_dockerfile_path = input("Enter the path to the Dockerfile: ")
            try:
                self._image_manager.build_image(image_name, image_dockerfile_path)
            except FileNotFoundError:
                print("No Dockerfile at this path")
        
        if user_input[COMMAND_INDEX] == "rmi":
            id = input("Enter the id of the image you want to remove: ")
            self._image_manager.delete_image(id)

        return True

    def run(self) -> None:
        """activate the DockerManager running"""
        print("*** Welcome to AD's POC Docker ***")
        is_running = True
        while is_running:
            is_running = self.interpret_command(self.get_input())

    def give_help(self) -> None:
        """function give help to user about the available commands"""
        print("---- help page ----")
        print("this are the available commands:")
        for command, describe in AVAILABLE_COMMANDS.items():
            if command not in [EXIT_COMMAND, HELP_COMMAND]:
                command = "docker " + command
            print(command, " - ", describe)

    def print_images(self):
        print(
            tabulate(
                [(image.name, image.creation_date, image.id) for image in self._image_manager.get_images()],
                headers=["Name", "Creation Date", "ID"],
                tablefmt="grid"
            )
        )
