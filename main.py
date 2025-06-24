from container_manager import ContainerManager
from docker_manager import DockerManager
from image_manager import ImageManager


def main():
    with ImageManager() as image_manager:
        DockerManager(image_manager, ContainerManager()).run()


if __name__ == "__main__":
    main()
