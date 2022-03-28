import os
from common.image import text_image


cwd = os.getcwd()

message = input("Insert your message here: ")
text_size = int(input("Size of text? Integers only: "))

filename = "audios/images/title.png"
# Create an image with white text on it in black blackground
text_image(
    message,
    filename=filename,
    width=3200,
    height=1800,
    text_size=text_size,
)

print(f"File saved in: {cwd}/{filename}")
