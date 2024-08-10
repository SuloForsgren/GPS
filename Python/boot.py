import math
import csv
import datetime
import serial
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # Ensure this matches your display
import time
from datetime import datetime

class LCDDisplay:
    def __init__(self):
        # Configuration for CS and DC pins
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)

        # Config for display baudrate (default max is 24mhz):
        BAUDRATE = 24000000

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()

        # Create the display:
        self.disp = st7735.ST7735R(
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
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  # we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width
            height = self.disp.height
        
        self.image = Image.new("RGB", (width, height))
        self.draw = ImageDraw.Draw(self.image)

        # Load a font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except IOError:
            self.font = ImageFont.load_default()

    def lcd_boot(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=(0, 0, 0))

        # Define the text to be drawn
        boot = f"Booting..."

        # Calculate text size and position using textbbox
        bbox = self.draw.textbbox((0, 0), boot, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        text_x = (self.image.width - text_width) // 2
        text_y = (self.image.height - text_height) // 8

        # Draw text onto the image
        self.draw.text((text_x, text_y), boot, font=self.font, fill=(255, 255, 255))

        # Display the image with text
        self.disp.image(self.image)
        time.sleep(2)

    def add_text(self, text, line_number):
        # Calculate the position based on the line number
        bbox = self.draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (self.image.width - text_width) // 2
        text_y = text_height * line_number + (line_number * 15)  # Add some spacing between lines

        # Draw new text onto the image
        self.draw.text((text_x, text_y), text, font=self.font, fill=(255, 255, 255))

        # Update the display with the new image
        self.disp.image(self.image)
        time.sleep(2)  # Adjust as needed

# Usage
lcd = LCDDisplay()
lcd.lcd_boot()  # Initial boot message

# Add additional text
lcd.add_text("Please,", 1)
lcd.add_text("wait!", 2)

