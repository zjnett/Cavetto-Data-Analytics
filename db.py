import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import datetime 
from random import randrange

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

# Main for testing
def database():
    cnx = connect()
    if cnx:
        # Query database
        cursor = cnx.cursor()
        query = ("SELECT * FROM `test_data`")
        cursor.execute(query)
        # Sample startdate
        start = datetime.datetime(2022, 3, 22,13,00)
        # Create empty pandas dataframe
        df = pd.DataFrame(columns=['value', 'time'])
        num_vals = cursor.rowcount
        i = 0
        for (value) in cursor:
            # Add value to pandas dataframe
            df_new_row = pd.DataFrame({'value' : value[0], 'time' : random_date(start)}, index=[i])
            df = pd.concat([df, df_new_row])
            i += 1
        return df, cnx
    return None, None