import math
import csv
import datetime
import serial
import time

def read_gps_data(log_file_path):
    SERIAL_PORT = '/dev/ttyAMA0'  # or '/dev/ttyAMA0' depending on your Raspberry Pi model
    BAUD_RATE = 9600
    # Open the serial port
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            # Read a line from the serial port
            line = ser.readline().decode('ascii', errors='replace').strip()
            
            if line.startswith('$GNRMC'):  # NMEA sentence starting with $GNRMC
                print(line)  # Print or process the line here
                with open(log_file_path, 'a') as file:
                    file.write("Log entry: {}\n".format(datetime.datetime.now()))
                    file.write(f"{line}\n")
            time.sleep(1)  # Adjust the sleep time as needed

def runMain(camStatus) :
    csv_file_path = "/home/sulof/GPS/Python/GPS/CamLocation/cams.csv"
    log_file_path = "/home/sulof/GPS/Python/GPS/Python/log.txt"
    
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            coord1 = float(row[0])
            coord2 = float(row[1])

            camera_coords = (coord1, coord2) #Read coords from the csv file!
            place_coords = (25.278768, 60.628445) #Get coords from gps device!
            
            # Calculate distance
            read_gps_data(log_file_path)
            distance = haversine_distance(camera_coords, place_coords)
            
            #Check if distance below 300m and then Alert!
            if (distance < 2) :
                while (distance > 0.01) :
                    distance -= 0.0166 #Just for testing
                    alert(distance, log_file_path)
                camStatus = True
                return camStatus
            
            #print(f"Geographic distance between camera and place: {distance:.5f} kilometers")
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

def alert(distance, log_file_path) :
    with open(log_file_path, 'a') as file:
        file.write("Log entry: {}\n".format(datetime.datetime.now()))
        file.write(f"{distance}\n")

def camCheck(camStatus, distance) :
    if (camStatus == False) :
        runMain(camStatus)
    else :
        alert(distance)


camStatus = False
distance = 0
camCheck(camStatus, distance)
