import pymysql
import pymysql.cursors
from math import radians, cos, sin, sqrt, atan2
import folium
import requests
import polyline

# Connect to the database
connection = pymysql.connect(
    host='localhost',
    port=3306,  # Port should be specified separately from the host
    user='root',
    password='123456',
    database='geopfe'
)


try:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""

  SELECT thing_id, trace_date, latitude, longitude, altitude, speed,gprmc_heading_deg, engine_status
  FROM trace_week
    WHERE thing_id = 3278 AND trace_date_day = '2024-03-02'
 ORDER BY date_insertion
    """)


finally:
    # Close the connection
    connection.close()

######################################################################################
# Initialize list to store tournes
tournes = []

# Initialize variables to store current tourne data
current_tourne = []
current_engine_status = None

# Iterate over the fetched rows
for row in cursor.fetchall():
    # Check if engine_status has changed
    if row['engine_status'] != current_engine_status:
        # If engine_status is 1 (active), start a new tourne
        if row['engine_status'] == 1:
            current_tourne = []  # Start a new tourne
            current_tourne.append(row)  # Add current row to the new tourne
            tournes.append(current_tourne)  # Append new tourne to the list of tournes
        # If engine_status is 0 (inactive) and current tourne is not empty, end the current tourne
        elif row['engine_status'] == 0 and current_tourne:
            current_tourne = []  # Clear the current tourne
    # If engine_status remains the same, continue adding points to the current tourne
    elif current_tourne:
        current_tourne.append(row)  # Add current row to the current tourne

    # Update current engine_status for the next iteration
    current_engine_status = row['engine_status']





tourne_1 = tournes[0]  # Assuming tourne 1 is the first tourne in the list

#print (tourne_1)

######################################################################################

def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate distance between two points on the earth (specified in decimal degrees)
    R = 6371000  # Radius of the earth in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def dead_reckoning(lat, lon, heading, speed, time_diff):
    # Calculate the new position based on speed, heading, and time difference
    # Heading in degrees, speed in m/s, and time_diff in seconds
    distance = speed * time_diff
    # Convert heading to radians
    heading = radians(heading)
    delta_lat = distance * cos(heading) / 6371000
    delta_lon = distance * sin(heading) / (6371000 * cos(radians(lat)))
    # Convert deltas from radians to degrees
    new_lat = lat + delta_lat * (180 / 3.141592)
    new_lon = lon + delta_lon * (180 / 3.141592)
    return new_lat, new_lon

# Assume tourne_1 is sorted by trace_date
new_points = []
for i in range(len(tourne_1) - 2):
    lat1 = float(tourne_1[i]['latitude'])
    lon1 = float(tourne_1[i]['longitude'])
    lat2 = float(tourne_1[i+1]['latitude'])
    lon2 = float(tourne_1[i+1]['longitude'])
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    if distance > 5:
        # Implement dead reckoning here if needed
        # Example: Assume speed and heading are available and reasonable
        speed = tourne_1[i]['speed']
        heading = tourne_1[i]['gprmc_heading_deg'] if tourne_1[i]['gprmc_heading_deg'] else 0
        # Calculate time difference in seconds
        time_diff = (tourne_1[i+1]['trace_date'] - tourne_1[i]['trace_date']).total_seconds()
        new_lat, new_lon = dead_reckoning(lat1, lon1, heading, speed, time_diff)
        new_points.append((new_lat, new_lon))



######################################################################################

m = folium.Map(location=[36.733706, 3.337851], zoom_start=13)


gpx_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
gpx_content += '<gpx version="1.1" creator="GraphHopper">\n<trk><name>GPS Data</name><trkseg>\n'
for point in tourne_1:
   gpx_content += f'    <trkpt lat="{point["latitude"]}" lon="{point["longitude"]}"></trkpt>\n'
#    gpx_content += f'    <trkpt lat="{point[0]}" lon="{point[1]}"></trkpt>\n'

gpx_content += '</trkseg></trk></gpx>'



def send_gpx_for_matching(gpx_content):
    """Send the GPX content to the GraphHopper Map Matching API and return the decoded points."""
    url = 'http://localhost:8989/match'
    params = {
        'profile': 'car',
        'type': 'json'
    }
    headers = {
        'Content-Type': 'application/gpx+xml'
    }
    response = requests.post(url, headers=headers, params=params, data=gpx_content)
    if response.status_code == 200:
        # Assuming the response contains the encoded polyline in a known structure
        matched_data = response.json()
        points = matched_data['paths'][0]['points']
        decoded_points = polyline.decode(points)
        return decoded_points
    else:
        raise Exception(f"Failed to get a valid response: {response.text}")

# Assuming you have generated the GPX content as before
decoded_points = send_gpx_for_matching(gpx_content)

# Use the decoded points as needed, for example, adding them to a Folium map
for point in decoded_points:
    lat, lon = point
    folium.Marker([lat, lon], icon=folium.Icon(color='green')).add_to(m)


# ########################################################################################################################################################
# Display original tourne points with enumeration
for idx, point in enumerate(tourne_1):
    folium.Marker(
        [float(point['latitude']), float(point['longitude'])],
        popup=f'Tourne Original Point {idx + 1}',
        icon=folium.Icon(color='blue')
    ).add_to(m)

# Display new points calculated by dead reckoning with enumeration
for idx, (lat, lon) in enumerate(new_points):
    folium.Marker(
        [lat, lon],
        popup=f'New Point {idx + 1}',
        icon=folium.Icon(color='purple')
    ).add_to(m)

# Display decoded points from GraphHopper with enumeration
for idx, (lat, lon) in enumerate(decoded_points):
    folium.Marker(
        [lat, lon],
        popup=f'Decoded Point {idx + 1}',
        icon=folium.Icon(color='green')
    ).add_to(m)

# ########################################################################################################################################################

m.save(r'C:\Users\SALAHPC\Documents\MYCODE\Results\map.html')