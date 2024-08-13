import math
import csv
import datetime
import serial
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
import time
from datetime import datetime

class data_handler():
    def __init__(self, data_type, index, serial) :
        self.data_type = data_type
        self.index = index
        self.serial = serial

    def parse_data(self, data):
        if data:
            parts = data.split(",")
            try:
                parsed_data = parts[self.index]
                return parsed_data
            except ValueError:
                pass
        return None

    def read_data(self):
        while True:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                if line.startswith(f"{self.data_type}"):
                    return self.parse_data(line)
        return None

class lcd_handler() :
    def __init__(self, data, cd_pin, dc_pin, reset_pin, baudrate) :
        self.data = data
        self.cs_pin = digitalio.DigitalInOut(cs_pin)
        self.dc_pin = digitalio.DigitalInOut(dc_pin)
        self.reset_pin = digitalio.DigitalInOut(reset_pin)
        self.baudrate = baudrate

    def screen_write(self) :
        spi = board.SPI()
        
        disp = st7735.ST7735R(
        spi,
        rotation=90,
        x_offset=0,
        y_offset=0,
        cs=self.cs_pin,
        dc=self.dc_pin,
        rst=self.reset_pin,
        baudrate=self.baudrate,)

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
        satellites = f"{self.data}"

        # Calculate text size and position using textbbox
        bbox = draw.textbbox((0, 0), satellites, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 7

        # Draw text onto the image
        draw.text((text_x, text_y), satellites, font=font, fill=(255, 255, 255))

        # Display the image with text
        disp.image(image)
        time.sleep(0.1)


gps_data_types = ["$GPGLL", "$GPGGA", "$GPRMC", "$GPVTG"]
gps_data_index = [6, 7, 3, 7]
index = 0

for gps_data_type in gps_data_types :
    with serial.Serial('/dev/serial0', 9600, timeout=0.1) as ser:
        data = data_handler(f"{gps_data_type}", gps_data_index[index], ser)
        parsed = data.read_data()
        print(parsed)
        index += 1

    cs_pin = board.CE0
    dc_pin = board.D25
    reset_pin = board.D24
    baudrate = 24000000

    write = lcd_handler(parsed, cs_pin, dc_pin, reset_pin, baudrate)
    write.screen_write()
