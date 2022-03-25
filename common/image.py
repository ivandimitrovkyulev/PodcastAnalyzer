from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)


def text_image(
        message: str,
        filename: str,
        width: int = 1600,
        height: int = 900,
        text_size: int = 30,
        image_color: str = 'black',
        text_color: str = 'white'
) -> None:
    """
    Saves an image with text on it.

    :param message: Message to display
    :param filename: Image filename to save as
    :param width: Image width
    :param height: Image height
    :param text_size: Text size in pt
    :param image_color: Image color
    :param text_color: Text color
    :return: None
    """

    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", text_size)

    img = Image.new('RGB', (width, height), color=image_color)

    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(message, font=font)

    center = (width-w)/2, (height-h)/2
    draw.text(center, message, fill=text_color, font=font)

    img.save(filename)


def text_to_image(
        message: str,
        existing_image: str,
        filename: str,
        text_size: int = 30,
        text_color: str = 'white'
) -> None:
    """
    Saves an image with text on it.

    :param message: Message to display
    :param existing_image: Name of existing image to write on
    :param filename: Image filename to save new image as
    :param text_size: Text size in pt
    :param text_color: Text color
    :return: None
    """

    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", text_size)

    img = Image.open(existing_image, 'r')
    draw = ImageDraw.Draw(img)

    width = img.size[0]
    height = img.size[1]
    w, h = draw.textsize(message, font=font)

    center = (width - w) / 2, (height - h) / 2
    draw.text(center, message, fill=text_color, font=font)

    img.save(filename)
