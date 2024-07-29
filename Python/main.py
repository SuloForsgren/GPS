import math
import csv

def runMain(camStatus) :
    csv_file_path = "H:\CameraTrack\GPS\CamLocation\cams.csv"
    
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            coord1 = float(row[0])
            coord2 = float(row[1])

            camera_coords = (coord1, coord2) #Read coords from the csv file!
            place_coords = (25.278768, 60.628445) #Get coords from gps device!
            
            # Calculate distance
            distance = haversine_distance(camera_coords, place_coords)
            
            #Check if distance below 300m and then Alert!
            if (distance < 2) :
                while (distance > 0.01) :
                    #distance -= 0.0166 Just for testing
                    alert(distance)
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

def alert(distance) :
    print(f">>>>>>>> {distance} <<<<<<<<")
    #if (distance < 0.01) :
    #    camStatus = False
    #    return camStatus 

def camCheck(camStatus, distance) :
    if (camStatus == False) :
        runMain(camStatus)
    else :
        alert(distance)


camStatus = False
distance = 0
camCheck(camStatus, distance)