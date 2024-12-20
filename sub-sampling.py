# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import combinations
import networkx as nx
#from scipy.spatial import cKDTree
from geopy.distance import geodesic
from collections import defaultdict
import random

# Constants
D_MAX = 11           # Maximum distance for co-location (meters)
P_INF = 0.1           # Infection probability
TIME_WINDOW = 900    # Time window for co-location (seconds)
INITIAL_INFECTED = 0.01  # Initial fraction of infected nodes
days_to_keep = 25









# Read File
# STEP 1: Load the Gowalla dataset
file_path = 'loc-gowalla_totalCheckins.txt/Gowalla_totalCheckins.txt'  # Replace with your dataset path

# Define column names based on Gowalla dataset format
columns = ['user_id', 'timestamp', 'latitude', 'longitude', 'location_id']

# Load the dataset
gowalla_data = pd.read_csv(file_path, sep='\t', names=columns, parse_dates=['timestamp'])
print("Dataset Loaded Successfully!")

# 指定起始日期
start_date = pd.Timestamp('2010-05-22 02:49:04+00:00')

# 往后读取25天的数据
end_date = start_date + pd.DateOffset(days=days_to_keep)
filtered_data = gowalla_data[gowalla_data['timestamp'] >= start_date]
filtered_data = filtered_data[filtered_data['timestamp'] <= end_date]








# Sampling
# Define the sampling rates
sampling_rates = [0.2, 0.1, 0.05, 0.025]

# Dictionaries to store user data for each sampling rate
user_data = [{} for _ in range(len(sampling_rates))]
sampled_dataset = [[] for _ in range(len(sampling_rates))]
sampled_user_counts = [0 for _ in range(len(sampling_rates))]

sample = {0.2: False, 0.1: False, 0.05: False, 0.025: False}
current_user_id = [-1 for _ in range(len(sampling_rates))]

for index, row in filtered_data.iterrows():
    user_id = row['user_id']
    checkin_time = row['timestamp']
    latitude = row['latitude']
    longitude = row['longitude']
    location_id = row['location_id']

    j = 0
    for i in sampling_rates:
        if sample[i] and user_id == current_user_id[j]:
            user_data[j][user_id].append((checkin_time, latitude, longitude, location_id))
            sampled_dataset[j].append((user_id, checkin_time, latitude, longitude, location_id))

        if user_id != current_user_id[j]:
            current_user_id[j] = user_id
            if random.random() < i:
                sample[i] = True
                user_data[j][user_id] = [(checkin_time, latitude, longitude, location_id)]
                sampled_dataset[j].append((user_id, checkin_time, latitude, longitude, location_id))
                sampled_user_counts[j] += 1
            else:
                sample[i] = False
        j += 1
        
for i in range(len(sampling_rates)):
    print("Sampling with rate", sampling_rates[i])
    print("Sampled user count for rate", sampling_rates[i], ":", sampled_user_counts[i])


