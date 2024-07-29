import math
import csv
import datetime
import serial

def read_gps_data(ser):
    """
    Reads GPS data from the serial port and extracts the relevant information.
    """
    # Read data from the serial port
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('$GPRMC'):  # You can check for other NMEA sentences if needed
            print(f"Received GPS data: {line}")
            return line
    return None

def parse_gps_data(data):
    # Example for parsing GPRMC sentence
    if data:
        parts = data.split(',')
        if len(parts) >= 6:
            lat = float(parts[3])
            lon = float(parts[5])
            return lat, lon
    return None, None

def calculateCoords(place_coords) :
    lat = place_coords[0]
    lon = place_coords[1]

    clat = lat[:1] + lat[2:] / 60
    clon = lon[:1] + lat[2:] / 60

    print(clat, clon)

def runMain(camStatus):
    csv_file_path = "/home/sulof/GPS/CamLocation/cams.csv"
    log_file_path = "/home/sulof/GPS/Python/log.txt"

    # Open the serial port
    with serial.Serial('/dev/serial0', 9600, timeout=1) as ser:
        while True:
            gps_data = read_gps_data(ser)
            if gps_data:
                place_coords = parse_gps_data(gps_data)
                if place_coords[0] is None or place_coords[1] is None:
                    continue

                else :
                    calculateCoords(place_coords)

                with open(csv_file_path, mode='r') as file:
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        coord1 = float(row[0])
                        coord2 = float(row[1])
                        camera_coords = (coord1, coord2)

                        # Calculate distance
                        distance = haversine_distance(camera_coords, place_coords)

                        # Check if distance is below threshold
                        if distance < 2:
                            while distance > 0.01:
                                distance -= 0.0166  # Just for testing
                                alert(distance, log_file_path)
                            camStatus = True
                            return camStatus

                # Break the loop if GPS data is not valid or other conditions
                break

    return camStatus

def haversine_distance(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

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

