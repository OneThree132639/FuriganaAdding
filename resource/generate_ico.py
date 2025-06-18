from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
input_img = os.path.join(script_dir, "icon.png")
output_icon = os.path.join(script_dir, "favicon.ico")

sizes = [(16, 16), (32, 32), (64, 64), (128, 128),
		 (256, 256)]

img = Image.open(input_img)
img.save(output_icon, format="ICO", sizes=sizes)