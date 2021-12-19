# lat_and_lon

### Introduction
This project solves the three sub tasks in the Task 1 as mentioned below:

Task 1: - Given "latitude_longitude_details.csv" as a list of latitude and longitudes from
Point A to Point B
1. Write a python code to find the latitude and longitude coordinates that are out of line and
automatically fix the same to form a continuous path.
2. From the given terrain list with kilometeres, write a python script to generate DB of each
latitude and longitude pair with matching terrain information (NB: take the starting
latitude and longitude and 0 KM and end as )
3. Write Query to list all the points with terrain “road” in it without “civil station”

### Getting Started
Task 1.1: The python code automatically fixes the latitude and longitude coordinates that are out of line from Point A to Point B.
This is done by calculating the distance between each (lat, lon), and checks if the distance between the lat lon exceeds the threshold distance.
Threshold is calculated by taking cumulative average of the distance from point A to the prev (lat, lon).
If the (lat, lon) exceeds the threshold distance, coordinate correction is made by calculating new (lat, lon) at a distance of threshold, in the same angle/projection of that of the correctecting (lat, lon). Geographiclib is the library used for distance and azimuth calculation.
Data is updated to table lat_long with corrected lat-lon.

Task 1.2: From given list of terrain with kilometers, each lat-lon is mapped to a terrain by comparing the cumulative distance of the lat-lon with that of the terrain.
Mapped terrain data is updated on the same table lat_long.

Task 1.3: Query to list all the point in the table lat_long with the terrain "road" in it without "civil station"

### Software dependencies
Python - 3.6 or above
Pandas - 1.0.1
SQLAlchemy - 1.3.13
Matplotlib - 3.3.4
Geographiclib - 1.52
