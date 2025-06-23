from image_manager import ImageManager


def main():
    with ImageManager("/tmp/docker_poc/") as image_manager:
        print("----- Run 1 -----")
        image_manager.build_image(name="test_image", dockerfile_path="/home/alonsd/dev/docker_poc/test/test_dockerfile.txt")
        for image in image_manager._images.values():
            print(image.creation_date)
        image_manager.save_images_to_files()
    with ImageManager("/tmp/docker_poc/") as image_manager:
        print("----- Run 2 -----")
        for image in image_manager._images.values():
            print(image.creation_date)


if __name__ == "__main__":
    main()
