import mysql.connector

# Open file and read credentials into config dictionary
def read_config(file):
    config = {}
    with open(file, 'r') as f:
        for line in f:
            (key, val) = line.strip().split('=')
            config[key] = val
    return config

    # Create a database

# Connect to the database
def connect():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="python_db"
    )
    return conn