import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # Ensure this matches your display

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the display:
disp = st7735.ST7735R(
    spi,
    rotation=90,
    x_offset=0,
    y_offset=0,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width
    height = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

# Load a font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except IOError:
    font = ImageFont.load_default()

# Define the text to be drawn
text = "Hello World"

# Calculate text size and position using textbbox
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
text_x = (width - text_width) // 2
text_y = (height - text_height) // 2

# Draw text onto the image
draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

# Display the image with text
disp.image(image)

# Optionally, load and scale another image
# image = Image.open("joyit-fox-widescreen.jpg")
# image_ratio = image.width / image.height
# screen_ratio = width / height
# if screen_ratio < image_ratio:
#     scaled_width = image.width * height // image.height
#     scaled_height = height
# else:
#     scaled_width = width
#     scaled_height = image.height * width // image.width
# image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
# x = scaled_width // 2 - width // 2
# y = scaled_height // 2 - height // 2
# image = image.crop((x, y, x + width, y + height))
# disp.image(image)

