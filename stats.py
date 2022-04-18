#!/usr/bin/env python3

import time
import datetime
import pandas as pd

def compile_24hr_dataframe(df):
    # Get the time of the latest data point
    latest_time = df['time'].max()
    # Filter dataframe to only include data from the last 24 hours
    df_24hr = df[df['time'] > latest_time - datetime.timedelta(hours=24)]
    # Return dataframe
    return df_24hr


def compute_statistics(df):
    # Construct df of just value as float
    df_value = df['value'].astype(float)
    # Compute statistics
    df_stats = df_value.describe()
    # Return statistics
    return df_stats

