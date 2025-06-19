#!/usr/bin/env python

from typing import List, Final

# Finals
EXIT_COMMAND: Final = 'exit'
HELP_COMMAND: Final = 'help'
COMMAND_PREFIX: Final = 'docker'
COMMAND_INDEX: Final = 1

AVIABALBE_COMMANDS = {EXIT_COMMAND: "Exit the program", HELP_COMMAND: "Get help",
                      "build": "Build an image from DockerFile.",
                      "run": "Creates and starts a new container from an image.",
                      "ps": "List all the existing containers.",
                      "images": "Lists all existing images.",
                      "stop": "Stops a running container.",
                      "rm": "Removes a stopped container.",
                      "rmi": "Removes an image."}

class DockerManager:
    """ The main Docker Manager - Docker Client """

    def __init__(self, image_manager, container_manager):
        self._image_manager = image_manager
        self._container_manager = container_manager
    
    def get_input(self) -> List[str]:
        """ function get the input from user
        :return: the user's input as list of words 
        """
        print("----$: ", end='')
        return input().split()
    
    def interpret_command(self, input: List[str]) -> bool:
        """ function interpret the input and call to the suitable handle function 
        :param input: list of the words in user's input line 
        :return: False if user want to exit, else True
        """
        if input[0].lower() == EXIT_COMMAND:
            return False
        
        if input[0].lower() == HELP_COMMAND:
            self.give_help()
            return True
        
        if input[0] != COMMAND_PREFIX:
            print("commands which not 'exit' or 'help' must start with '", COMMAND_PREFIX, "' prefix")
            return True
        
        if input[COMMAND_INDEX] not in AVIABALBE_COMMANDS.keys():
            print("command", input[COMMAND_INDEX], "is unknown")

        return True

    def run(self) -> None:
        """ activate the DockerManager running """
        print("*** Welcome to AD's POC Docker ***")
        is_running = True
        while is_running:
            is_running = self.interpret_command(self.get_input())
    
    def give_help(self) -> None:
        """ function give help to user about the aviable commands """
        print("---- help page ----")
        print("this are the aviable commands:")
        for command, describe in AVIABALBE_COMMANDS.items():
            if command not in [EXIT_COMMAND, HELP_COMMAND]:
                command = "docker " + command
            print(command, " - ", describe)
