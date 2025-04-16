# image_processor.py
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Processes an image file.")
    parser.add_argument("--input_image", type=str, required=True, help="The image file to process")
    args = parser.parse_args()

    image_file = args.input_image
    print(image_file)

if __name__ == "__main__":
    main()