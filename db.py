from socket import NI_NAMEREQD
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import datetime 
from random import randrange

def generate_random_dates(n_dates):
    start = datetime.datetime(2022, 3, 22,13,00)
    dates = []
    for i in range(n_dates):
        dates.append(random_date(start))
    return dates

# Open file and read credentials into config dictionary
def read_config(file):
    config = {}
    with open(file, 'r') as f:
        for line in f:
            (key, val) = line.strip().split('=')
            config[key] = val
    return config

# Connect to the database
def connect():
    config = read_config("config/database.ini") # hardcoded for now
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
        return cnx
    return None

# Generate random time
def random_date(start):
    start = start + datetime.timedelta(minutes=randrange(60))
    return start

def get_num_data_points():
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `test_data`")
        cursor.execute(query)
        num_vals = cursor.rowcount
        cnx.close()
        return num_vals
    return None

# Main for testing
def database(table_name):
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `{}`".format(table_name))
        cursor.execute(query)
        # Create empty pandas dataframe
        df = pd.DataFrame(columns=['value', 'time'])
        num_vals = cursor.rowcount
        i = 0
        for (value) in cursor:
            # Add value to pandas dataframe
            df_new_row = pd.DataFrame({'value' : value[1], 'time' : value[2]}, index=[i])
            df = pd.concat([df, df_new_row])
            i += 1
        cnx.close()
        return df
    return None

# Retrieve thermal image from database and save it to static directory
def save_last_thermal_image():
    # Connect to database
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `thermal_images` ORDER BY `time` DESC LIMIT 1")
        cursor.execute(query)
        # Write blob as static image
        for (value) in cursor:
            with open('assets/thermal_image.jpg', 'wb') as f:
                f.write(value[1])
            min, max = value[3], value[4]
        cnx.close()
        return min, max
    return None, None # Return temperature (min, max)

# Retrieve RGB image from database and save it to static directory
def save_last_rgb_image():
    # Connect to database
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `rgb_images` ORDER BY `time` DESC LIMIT 1")
        cursor.execute(query)
        # Write blob as static image
        for (value) in cursor:
            with open('assets/rgb_image.jpg', 'wb') as f:
                f.write(value[1])
            time = value[2]
        cnx.close()
        return time
    return None

# Read box string of most recent data point in boxes table and return it
def read_boxes():
    time = None
    box_string = None
    # Connect to database
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `boxes` ORDER BY `time` DESC LIMIT 1")
        cursor.execute(query)
        for (value) in cursor:
            time = value[1]
            box_string = value[2]
        cnx.close()
    return time, box_string
