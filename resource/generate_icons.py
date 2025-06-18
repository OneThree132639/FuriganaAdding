from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
src_image = os.path.join(script_dir, "icon.png")
output_dir = os.path.join(script_dir, "myicon.iconset")

icon_sizes = [
	(16, 16), (32, 32), (64, 64), (128, 128),
	(256, 256), (512, 512)
]

def main():
	os.makedirs(output_dir, exist_ok=True)

	img = Image.open(src_image)

	for size in icon_sizes:
		logical_size = size[0]
		actual_size = size[0]
		actual_size_2x = size[0]*2

		img_resized = img.resize((actual_size, actual_size), Image.Resampling.LANCZOS)
		filename = "icon_{}x{}.png".format(logical_size, logical_size)
		img_resized.save(os.path.join(output_dir, filename))
		print("[Saved] {}".format(filename))

		if actual_size_2x <= 1024:
			img_resized_2x = img.resize((actual_size_2x, actual_size_2x), Image.Resampling.LANCZOS)
			filename_2x = "icon_{}x{}@2x.png".format(logical_size, logical_size)
			img_resized_2x.save(os.path.join(output_dir, filename_2x))
			print("[Saved] {}".format(filename_2x))

if __name__ == "__main__":
	main()