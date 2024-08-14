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
    def __init__(self, serial) :
        self.serial = serial

    def read_full_data(self):
        while True:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                return line
        return None

    def parse_data(self, data):
        if data:
            parts = data.split(",")
            if len(parts) >= 8:  # Adjust based on how many fields you expect
                return parts
        return None

class lcd_handler() :
    def __init__(self, cs_pin, dc_pin, reset_pin, baudrate) :
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
            baudrate=self.baudrate,
        )

        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width  # we swap height/width to rotate it to landscape!
            self.width = self.disp.height
        else:
            self.width = self.disp.width
            self.height = self.disp.height

        # Initialize the image and drawing context
        self.image = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)

        # Clear the screen initially
        self.clear_screen()

    def clear_screen(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        # Update the display
        self.disp.image(self.image)

    def screen_write(self, data, line_number) :
        # Define the text to be drawn
        write_data = f"{data}"

        # Calculate text size and position using textbbox
        bbox = self.draw.textbbox((0, 0), write_data, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Adjust the vertical position based on the line number
        text_x = (self.width - text_width) // 2
        text_y = (text_height + 5) * line_number

        # Draw text onto the image
        self.draw.text((text_x, text_y), write_data, font=self.font, fill=(255, 255, 255))

        # Update the display with the new image
        self.disp.image(self.image)
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
                coord1 = float(row[1])
                coord2 = float(row[0])
                camera_coords = (coord1, coord2)

                distance = self.haversine_distance(camera_coords, self.location_coords)
                
                if distance < lowest_dist :
                    lowest_dist = distance

            return lowest_dist

def convert_to_decimal(degrees_minutes, directions):
    decimals = []

    for index, coord in enumerate(degrees_minutes):
        coord = str(coord)

        # Convert from degrees and minutes to decimal degrees
        degrees = int(coord[:2])
        minutes = float(coord[2:])

        # Convert to decimal degrees
        decimal_degrees = degrees + (minutes / 60.0)

        # Apply direction
        if directions[index] in ['S', 'W']:
            decimal_degrees = -decimal_degrees

        decimals.append(decimal_degrees)

    return tuple(decimals)
  
csv_file_path = "/home/sulof/GPS/CamLocation/cams.csv"
went_past = False
while True:
    with serial.Serial('/dev/ttyACM0', 9600, timeout=0.1) as ser:
        data_handler_instance = data_handler(ser)
        full_data = data_handler_instance.read_full_data()
        parsed_data = data_handler_instance.parse_data(full_data)

        if parsed_data:
            print(parsed_data)

            cs_pin = board.CE0
            dc_pin = board.D25
            reset_pin = board.D24
            baudrate = 24000000

            write = lcd_handler(cs_pin, dc_pin, reset_pin, baudrate)

            if parsed_data[2] == "V":
                write.screen_write("No GPS fix", 0)
            elif parsed_data[2] == "A" and len(parsed_data) >= 7:
                place_coords = (float(parsed_data[3]), float(parsed_data[5]))
                directions = (parsed_data[4], parsed_data[6])
                place_coords = convert_to_decimal(place_coords, directions)

                distance = calculate(place_coords, csv_file_path)
                to_cam = distance.read_csv()
                kilometers = str(to_cam)
                kilometers = int(kilometers[0])
                meters = str(to_cam).split(".")[1]
                meters = meters[:3]
                print(meters)
                speed = 1.852 * float(parsed_data[7])
                speed = round(speed)
                meters = int(meters)

                if meters < 300 and not went_past:
                    # Display approaching message when entering radius
                    write.screen_write("Kamera", 0)
                    write.screen_write("lähestyy!", 1)
                    write.screen_write(f"{meters} m", 2)
                    went_past = True  # Set went_past to True
                    time.sleep(0.1)
                elif meters > 300 and went_past:
                    # Reset went_past when leaving radius
                    went_past = False
                else:
                    # Display distance and speed when outside radius
                    if kilometers >= 1:
                        write.screen_write(f"{kilometers} km", 0)
                    write.screen_write(f"{meters} m", 1)
                    write.screen_write(f"{speed} km/h", 2)
                    time.sleep(0.4)