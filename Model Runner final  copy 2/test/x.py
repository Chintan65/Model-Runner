import json
from PIL import Image, ImageDraw
import uuid

# Load parameter definitions
with open('params.json') as f:
    params = json.load()

# Collect user input based on definitions
values = []
for p in params['input_parameters']:
    val = float(input(f"Enter {p['description']}: "))
    values.append(val)

total = sum(values)
text = f"Sum = {total}"

# Create and save image
img = Image.new('RGB', (300, 100), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.text((10, 40), text, fill=(255, 255, 255))
filename = f"sum_{uuid.uuid4().hex[:8]}.png"
img.save(filename)

print(filename)
