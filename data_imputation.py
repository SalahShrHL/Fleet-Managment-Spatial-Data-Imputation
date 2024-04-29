import pymysql
import pymysql.cursors
from math import radians, cos, sin, sqrt, atan2
import folium
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