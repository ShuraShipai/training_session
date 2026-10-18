
from rembg import remove

input_path = "/Users/shurashipai/Projects/training_sessions/Image.jpeg"
output_path = "output.png"

with open(input_path, "rb") as input_file:
    input_bytes = input_file.read()

# Remove background
output_bytes = remove(input_bytes)

# Save the output image
with open(output_path, "wb") as output_file:
    output_file.write(output_bytes)

print("Background removed successfully!")
