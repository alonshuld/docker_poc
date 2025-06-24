from image_manager import ImageManager


def print_images(image_manager: ImageManager):
    for image in image_manager.get_images():
        print(image)


def main():
    with ImageManager() as image_manager:
        print("----- Run 1 -----")
        image_manager.build_image(
            image_name="test_image", dockerfile_path="/home/alonsd/dev/docker_poc/test/test_dockerfile.txt"
        )
        print_images(image_manager)
        image_manager.save_images_to_files()
    with ImageManager() as image_manager:
        print("----- Run 2 -----")
        print_images(image_manager)


if __name__ == "__main__":
    main()
