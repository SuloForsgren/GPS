import math
import csv
import datetime
import serial
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # Ensure this matches your display
import time

def lcd_write(speed, distance):
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
    text = f"{int(speed)}Km/h"
    distance_text = f"{int(distance)}Km"

    # Calculate text size and position using textbbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    text_x = (width - text_width) // 1
    text_y = (height - text_height) // 7

    distance_x = (width - text_width) // 2
    distance_y = (height - text_height) // 3

    # Draw text onto the image
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    draw.text((distance_x, distance_y), distance_text, font=font, fill=(255, 255, 255))

    # Display the image with text
    disp.image(image)

    time.sleep(1.5)

def read_gps_data(ser):
    """
    Reads GPS data from the serial port and extracts the relevant information.
    """
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('$GPRMC'):
            print(f"Received GPS data: {line}")
            return line
    return None

def parse_gps_data(data):
    """
    Parses the GPRMC sentence to extract latitude and longitude.
    """
    if data:
        parts = data.split(",")
        if len(parts) >= 6 and parts[3] and parts[5]:
            try:
                lat = float(parts[3])
                lon = float(parts[5])
                return lat, lon
            except ValueError:
                pass
    return None, None

def calculateSpeed(speed):
    if (speed == "") :
        return 0
    calculatedSpeed = float(speed) * 1.85200
    print(calculatedSpeed)
    return calculatedSpeed

def get_speed(gps_data):
    if gps_data:
        parts = gps_data.split(",")
        speed = parts[7]
        speed = calculateSpeed(speed)
        return speed
    

def calculateCoords(place_coords):
    """
    Converts GPS coordinates from NMEA format to decimal degrees.
    """
    lat = place_coords[0]
    lon = place_coords[1]

    # Split the latitude into degrees and minutes
    lat_deg = int(lat // 100)
    lat_min = lat % 100

    # Split the longitude into degrees and minutes
    lon_deg = int(lon // 100)
    lon_min = lon % 100

    # Convert to decimal degrees
    clat = lat_deg + (lat_min / 60.0)
    clon = lon_deg + (lon_min / 60.0)

    return clat, clon

def runMain(camStatus):
    csv_file_path = "/home/sulof/GPS/CamLocation/cams.csv"
    log_file_path = "/home/sulof/GPS/Python/log.txt"

    with serial.Serial('/dev/serial0', 9600, timeout=1) as ser:
        while True:
            gps_data = read_gps_data(ser)
            if gps_data:
                place_coords = parse_gps_data(gps_data)
                speed = get_speed(gps_data)
                if place_coords[0] is None or place_coords[1] is None:
                    continue

                place_coords = calculateCoords(place_coords)

                with open(csv_file_path, mode='r') as file:
                    lowestDist = 10000
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        coord1 = float(row[0])
                        coord2 = float(row[1])
                        camera_coords = (coord1, coord2)
                        #lcd_write(speed)

                        # Calculate distance
                        distance = haversine_distance(camera_coords, place_coords)

                        if distance < lowestDist :
                            lowestDist = distance

                        # Check if distance is below threshold
                        if distance < 0.3:  # 300 meters threshold
                            log_proximity(camera_coords, place_coords, distance, log_file_path)
                            while distance > 0.01:
                                distance -= 0.0166  # Just for testing
                                alert(distance, log_file_path)
                            camStatus = True
                            return camStatus
                    
                    lcd_write(speed,lowestDist)
                break

    return camStatus

def haversine_distance(coord1, coord2):
    """
    Calculates the Haversine distance between two sets of (lat, lon) coordinates.
    """
    R = 6371.0  # Radius of the Earth in kilometers

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def log_proximity(camera_coords, place_coords, distance, log_file_path):
    """
    Logs the proximity event to a file.
    """
    with open(log_file_path, 'a') as file:
        log_time = datetime.datetime.now()
        file.write(f"Log entry: {log_time}\n")
        file.write(f"Camera coordinates: {camera_coords}\n")
        file.write(f"Current coordinates: {place_coords}\n")
        file.write(f"Distance: {distance:.5f} km\n")
        file.write("\n")

def alert(distance, log_file_path):
    with open(log_file_path, 'a') as file:
        file.write("Log entry: {}\n".format(datetime.datetime.now()))
        file.write(f"{distance}\n")

def camCheck(camStatus):
    if not camStatus:
        runMain(camStatus)
    else:
        alert(distance, log_file_path)

camStatus = False
distance = 0
camCheck(camStatus)
  
