import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import traceback
from geographiclib.geodesic import Geodesic

geod = Geodesic.WGS84

engine = create_engine('mysql://<connection_string>')


def plot_coords(df):
    """
    Function to plot the data points: latitude and longitude
    :param df: data points in dataframe
    :return:
    """
    try:
        print(df.shape)
        plt.scatter(df['longitude'], df['latitude'])
        plt.show()
        # plt.plot(df['longitude'], df['latitude'])
        # plt.show()
        print("---->>>> Plot coordinates")
        return
    except:
        print("Error in reading CSV: ", traceback.format_exc())
        raise


def create_tables():
    """
    Drop and create table "lat_long" to update the datapoints
    :return:
    """
    try:
        lat_long = text('Drop table if exists lat_long; '
                        'CREATE TABLE if not exists lat_long  '
                            '(pk_id int primary key AUTO_INCREMENT, '
                            'latitude float NOT NULL, '
                            'longitude float NOT NULL, '
                            'distance float, '
                            'cumulative_distance float, '
                            'terrain varchar(50));')
        engine.execute(lat_long)
        print("---->>>> Created table lat_long")
        return
    except:
        print("Error in creating table: ", traceback.format_exc())
        raise


def coordinate_correction(azi1, threshold, lat1, lon1):
    """
    Correcting the coordinate (lat2, lon2) by finding a new lat and lon from (lat1, lon1) in the same direction as the
    (lat2, lon2) in a given distance.
    :param azi1: projection of (lat2, lon2) from (lat1, lon1)
    :param threshold: distance at which new lat and lon should be found from (lat1, lon1)
    :param lat1: latitude from which new latitude has to be calculated at an angle of azi1, at a distance "threshold"
    :param lon1: longitude from which new longitude has to be calculated at an angle of azi1, at a distance "threshold"
    :return: new latitude and longitude calculated - dir['lat2'], dir['lon2']
    """
    try:
        dir = geod.Direct(lat1, lon1, azi1, threshold)
        return dir['lat2'], dir['lon2']
    except Exception:
        print("Error in modifying lat long: ", traceback.format_exc())
        return



def insert_data(lat2, lon2, dist, cum_dist):
    """
    Insert data with corrected lat and lon
    :param lat2: latitude
    :param lon2: longititude
    :param dist: distance between (lat2, lon2) from the previous lat and lon
    :param cum_dist: cumulative distance
    :return:
    """
    try:
        dc_query = text(
            'Insert into lat_long (latitude, longitude, distance, cumulative_distance) '
            'values(:lat2, :lon2, :dist, :cum_dist);')
        engine.execute(dc_query, lat2 = lat2, lon2 = lon2, dist = dist, cum_dist = cum_dist)
        print("---->>>> Insert data to lat_long table")
        return
    except:
        print("Error in inserting data to table:: ", traceback.format_exc())
        raise


def coordinate_processing(df):
    """
    Coordinate correction
    :param df: data source
    :param dist: distance between 2 (lat,lon) in km
    :param threshold: threshold in km is the distance above which the (lat, lon) is corrected
    :return:
    """
    try:
        lat1 = df['latitude'][0]
        lon1 = df['longitude'][0]
        cum_dist = 0
        for indx, row in df.iterrows():
            lat2 = row['latitude']
            lon2 = row['longitude']
            g = geod.Inverse(lat1, lon1, lat2, lon2)
            dist = round(g['s12']/1000, 6)
            if indx <= 2:
                threshold = dist    # Until first three coordinates is obtained, threshold is taken as the distance between 2 (lat, lon)
            else:
                threshold = cum_dist / (indx - 1)   # threshold is calculated by taking average of distances between two (lat, lon) untill prev (lat, lon)
            print(f"lat2: {lat2} \tlon2: {lon2} \tdist::: {dist} \tthreshold: {threshold} \tcum: {cum_dist+dist}")
            if dist > threshold:
                lat2, lon2 = coordinate_correction(g['azi1'], threshold * 1000, lat1, lon1)
                print(f"lat2: {lat1} \tlon2: {lon2} \tdist::: {dist} \tthreshold: {threshold} \tcum: {cum_dist+dist}")
                dist = threshold
            cum_dist += dist
            insert_data(lat2, lon2, dist, cum_dist)
            lat1 = lat2
            lon1 = lon2
        print("---->>>> Coordinates corrected")
        return df
    except Exception:
        print("Error in coordinate correction: ", traceback.format_exc())
        return


def update_data(pk_id, terrain):
    """
    Update data in table with the terrain details
    :param pk_id: primary key in table to which data needs to updated with terrain details
    :param terrain: terrain detail for each (lat, lon)
    :return:
    """
    try:
        dc_query = text(
            'Update lat_long set terrain = :terrain where pk_id = :pk_id;')
        engine.execute(dc_query, terrain=terrain, pk_id=pk_id)
        print("---->>>> Data updated to lat_long table")
    except:
        print("Error in updating table: ", traceback.format_exc())


def map_terrain():
    """
    Task 1.2: Fetch data from table and map the terrains in the data file 'terrain_classification_test.csv' to each (lat, lon)
    :return:
    """
    try:
        df = pd.read_sql('SELECT * FROM lat_long', con=engine)
        terrain_df = pd.read_csv("terrain_classification_test.csv")
        terrains = terrain_df['terrain'].tolist()
        kms = terrain_df['distance (in km)'].tolist()
        kms, terrains = zip(*sorted(zip(kms, terrains), reverse=True))
        for indx, row in df.iterrows():
            for index, km in enumerate(kms):
                if row['cumulative_distance'] >= km:
                    update_data(row['pk_id'], terrains[index])
                    break
        print("---->>>> Terrain mapped")
        return
    except Exception:
        print("Error in mapping territory: ", traceback.format_exc())
        raise


def get_road_terrain():
    """
    Task 1.3: Fetch data from table to list all points with terrain "road" in it without "civil station"
    :return:
    """
    try:
        rd_t = text('select * from lat_long where terrain like :str1 and terrain not like :str2;')
        rd_t = engine.execute(rd_t, str1 = '%road%', str2 = '%civil station%')
        for t in rd_t:
            print("latitude: ", t.latitude, ",\t longitude: ", t.longitude, ",\t terrain: ", t.terrain)
        print("---->>>> Fetched Road Terrain")
    except Exception:
        print("Error in getting road terrain ", traceback.format_exc())
        raise


def main():
    try:
        # Task 1.1
        df = pd.read_csv("latitude_longitude_details.csv")
        plot_coords(df)
        create_tables()
        # coordinate_correction_test(df)
        coordinate_processing(df)
        map_terrain()   # Task 1.2
        get_road_terrain()    # Task 1.3
        print("---->>>> Done")
    except Exception:
        print("Error::: ", traceback.format_exc())
        return


main()
