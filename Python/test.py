def calculateCoords(place_coords):
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

    print(f"Latitude: {clat}, Longitude: {clon}")

coords = (6039.58483, 2512.25610)
calculateCoords(coords)
