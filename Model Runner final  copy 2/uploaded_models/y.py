import os
import sys


image_input = sys.argv[1]
new_name = sys.argv[2]


ext = os.path.splitext(image_input)[1]
new_filename = new_name + ext


os.rename(image_input, new_filename)


print(os.path.abspath(new_filename))
