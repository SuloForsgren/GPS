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
                if parsed_data == "" :
                    return "Empty"
                else :
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
    def __init__(self, cd_pin, dc_pin, reset_pin, baudrate) :
        self.cs_pin = digitalio.DigitalInOut(cs_pin)
        self.dc_pin = digitalio.DigitalInOut(dc_pin)
        self.reset_pin = digitalio.DigitalInOut(reset_pin)
        self.baudrate = baudrate
        self.spi = board.SPI()
        
        self.disp = st7735.ST7735R(
        self.spi,
        rotation=90,
        x_offset=0,
        y_offset=0,
        cs=self.cs_pin,
        dc=self.dc_pin,
        rst=self.reset_pin,
        baudrate=self.baudrate,)


    def screen_write(self, data) :
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  # we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width
            height = self.disp.height
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
        write_data = f"{data}"

        # Calculate text size and position using textbbox
        bbox = draw.textbbox((0, 0), write_data, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 7

        # Draw text onto the image
        draw.text((text_x, text_y), write_data, font=font, fill=(255, 255, 255))

        # Display the image with text
        self.disp.image(image)
        time.sleep(0.1)

class calculate():
    def __init__(self, location_coords, csv_file_path):
        self.location_coords = location_coords
        self.csv_file_path = csv_file_path

    def haversine_distance(self, coord1, coord2):
        R = 6371.0

        lat1, lon1 = float(coord1[0]), float(coord1[1])
        lat2, lon2 = float(coord2[0]), float(coord2[1])

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance

    def read_csv(self):
        with open(self.csv_file_path, mode='r') as file:
            lowest_dist = float('inf')
            csv_reader = csv.reader(file)
            for row in csv_reader:
                coord1 = float(row[0])
                coord2 = float(row[1])
                camera_coords = (coord1, coord2)

                distance = self.haversine_distance(camera_coords, self.location_coords)
                
                if distance < lowest_dist :
                    lowest_dist = distance

            return lowest_dist

# 1. Valid data? 2. Satellites 3. Latitude? 4. Speed?
gps_data_types = ["$GPGLL", "$GPGLL", "$GPGLL", "$GPGGA", "$GPRMC", "$GPVTG"]
gps_data_index = [6, 1, 3, 7, 3, 7]
index = 0
parsed_data = []
csv_file_path = "/home/sulof/GPS/CamLocation/cams.csv"


while True:
    for gps_data_type in gps_data_types :
        with serial.Serial('/dev/ttyACM0', 9600, timeout=0.1) as ser:
            if index == 6 :
                index = 0
            data = data_handler(f"{gps_data_type}", gps_data_index[index], ser)
            parsed = data.read_data()
            if len(parsed_data) < 6 :
                parsed_data.append(parsed)
            elif len(parsed_data) >= 6 :
                parsed_data[index] = parsed
            print(parsed_data)
            index += 1

            cs_pin = board.CE0
            dc_pin = board.D25
            reset_pin = board.D24
            baudrate = 24000000

            write = lcd_handler(cs_pin, dc_pin, reset_pin, baudrate)
            """if parsed_data[0] == "V" and len(parsed_data) > 1:
                helper = 0
                for type in gps_data_types :
                    if type == "$GPGGA" and len(parsed_data) > 3:
                        write.screen_write(parsed_data[helper])
                    helper += 1
            elif parsed_data[0] == "A" and len(parsed_data) > 3 :
                #write.screen_write(parsed_data[-1])
                place_coords = (float(parsed_data[1]), float(parsed_data[2]))
                print(place_coords)
                distance = calculate(place_coords, csv_file_path)
                to_cam = distance.read_csv()
                to_cam = round(to_cam, 2)
                write.screen_write(to_cam)
            """

            place_coords = (60.627886, 25.251083)
            distance = calculate(place_coords, csv_file_path)
            to_cam = distance.read_csv()
            to_cam = round(to_cam)
            kilometers = round(to_cam/1000)
            meters = to_cam%1000
            write.screen_write(f"{kilometers} km")
