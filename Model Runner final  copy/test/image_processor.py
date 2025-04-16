# image_processor.py
import argparse
import os
from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Processes an image file.")
    parser.add_argument("--input_image", type=str, required=True, help="The image file to process")
    args = parser.parse_args()

    image_file = args.input_image
    # print(image_file)

    plt.plot([1, 2, 3], [4, 5, 6])
    plt.savefig('chart.png')
    print('chart.png')

if __name__ == "__main__":
    main()