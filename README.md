# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import combinations
import networkx as nx
#from scipy.spatial import cKDTree
from geopy.distance import geodesic

# Constants
D_MAX = 11           # Maximum distance for co-location (meters)
P_INF = 0.1           # Infection probability
TIME_WINDOW = 900    # Time window for co-location (seconds)
INITIAL_INFECTED = 0.01  # Initial fraction of infected nodes
SAMPLING_PROPORTIONS = np.array([0.025, 0.05, 0.1, 0.2])  # Sampling proportions (0.025, 0.05, 0.1, 0.2)

# STEP 1: Load the Gowalla dataset
file_path = 'loc-gowalla_totalCheckins.txt/Gowalla_totalCheckins.txt'  # Replace with your dataset path

# Define column names based on Gowalla dataset format
columns = ['user_id', 'timestamp', 'latitude', 'longitude', 'location_id']

# Load the dataset
gowalla_data = pd.read_csv(file_path, sep='\t', names=columns, parse_dates=['timestamp'])
# Convert dataset timestamp to datetime objects
gowalla_data['timestamp'] = pd.to_datetime(gowalla_data['timestamp'])
# Remove rows with any column equal to 0
gowalla_data = gowalla_data[(gowalla_data != 0).all(axis=1)]
# Reset index after dropping rows
gowalla_data.reset_index(drop=True, inplace=True)

for sampling_fraction in SAMPLING_PROPORTIONS:
    # Perform sampling by user_id
    sampled_data = gowalla_data.groupby('user_id', group_keys=False).apply(lambda x: x.sample(frac=sampling_fraction))
    file_name = f'sampled_data_{sampling_fraction}.txt'
    sampled_data.to_csv(file_name, sep='\t', index=False)
    print(f"Data sampled at {sampling_fraction} proportion saved to {file_name}")

print("Dataset Loaded Successfully!")
