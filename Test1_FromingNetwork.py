# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import combinations
import networkx as nx
from scipy.spatial import cKDTree

# Constants
D_MAX = 110           # Maximum distance for co-location (meters)
P_INF = 0.1           # Infection probability
TIME_WINDOW = 1920    # Time window for co-location (seconds)
INITIAL_INFECTED = 0.01  # Initial fraction of infected nodes
SAMPLING_PROPORTIONS = [0.025,0.05,0.1,0.2]  # Sampling proportions

# STEP 1: Load the Gowalla dataset
file_path = 'loc-gowalla_totalCheckins.txt/Gowalla_totalCheckins.txt'  # Replace with your dataset path

# Define column names based on Gowalla dataset format
columns = ['user_id', 'timestamp', 'latitude', 'longitude', 'location_id']


# Load the dataset
gowalla_data = pd.read_csv(file_path, sep='\t', names=columns, parse_dates=['timestamp'])
print("Dataset Loaded Successfully!")

# 指定起始日期
start_date = pd.Timestamp('2010-10-1 00:00:00+00:00')


# 往后读取20天的数据
end_date = start_date + pd.DateOffset(days=20)
period_data = gowalla_data[(gowalla_data['timestamp'] >= start_date) & (gowalla_data['timestamp'] <= end_date)]
print("Dataset period filtered Successfully!")

# Identify the top 20000 unique user_id
top_user_ids = period_data['user_id'].value_counts().index[:20000]

# Filter data based on the top 20000 user_id
dataset = period_data[period_data['user_id'].isin(top_user_ids)]

# Calculate the final number of rows in the filtered dataset
final_data_size = len(dataset)
unique_user_ids = dataset['user_id'].nunique()

gowalla_data = dataset.loc[(dataset['latitude'] >= -90) & (dataset['latitude'] <= 90) & 
                                   (dataset['longitude'] >= -180) & (dataset['longitude'] <= 180)]

print(f"Final dataset size: {final_data_size} rows")
print(f"Number of unique user_id in the final dataset: {unique_user_ids}")




def build_contact_network_optimized(data, d_max=D_MAX, time_window=TIME_WINDOW):
    """
    Build a collection of contact networks using spatial and temporal optimizations.
    """
    G = {}  # Dictionary to store contact networks for each time window
    
    # Sort data by timestamp for efficient grouping
    data = data.sort_values(by='timestamp')
    
    # Group data into time windows
    min_time = data['timestamp'].min()
    data['time_bucket'] = ((data['timestamp'] - min_time).dt.total_seconds() // time_window).astype(int)
    grouped = data.groupby('time_bucket')
    k=0
    # Process each time bucket
    for time_bucket, group in grouped:
        # Create a KDTree for spatial indexing within the current time window
        coords = group[['latitude', 'longitude']].values
        tree = cKDTree(coords)
        
        # Create a new network for this time window
        G[time_bucket] = nx.Graph()
        # Find all pairs of users within the distance threshold for this tree
        pairs = tree.query_pairs(d_max / 1000)
        for i, j in pairs:
            coords_user1 = group[['latitude', 'longitude']].iloc[i]
            coords_user2 = group[['latitude', 'longitude']].iloc[j]
            distance = geodesic((coords_user1['latitude'], coords_user1['longitude']), (coords_user2['latitude'], coords_user2['longitude'])).meters
            
            if distance < D_MAX:  # Check if the distance is less than 110 meters
                user1, user2 = group['user_id'].values[i], group['user_id'].values[j]
                G[time_bucket].add_edge(user1, user2)
    
    return G
# Example usage
contact_graph = build_contact_network_optimized(gowalla_data)
print("Contact Graph Generated Successfully!")


'''
def plot_graph_with_edges_only_rowwise(contact_graph, num_graphs=10, graphs_per_row=2):
    num_rows = num_graphs // graphs_per_row + (num_graphs % graphs_per_row > 0)
    fig, axs = plt.subplots(num_rows, graphs_per_row, figsize=(15, 5 * num_rows))

    for i, (time_bucket, G_network) in enumerate(contact_graph.items()):
        if i >= num_graphs:
            break

        row = i // graphs_per_row
        col = i % graphs_per_row

        edges = list(G_network.edges())
        nodes_with_edges = set([n for e in edges for n in e])

        G_subgraph = G_network.subgraph(nodes_with_edges)

        ax = axs[row, col] if num_rows > 1 else axs[col]
        ax.set_title(f"Contact Network - Time Window {time_bucket}")

        nx.draw(G_subgraph, with_labels=True, node_color='skyblue', node_size=30, edge_color='gray', ax=ax)

    for i in range(num_graphs, num_rows*graphs_per_row):
        fig.delaxes(axs.flatten()[i])

    plt.tight_layout()
    plt.show()

# Assuming contact_graph is a dictionary containing contact networks
plot_graph_with_edges_only_rowwise(contact_graph, num_graphs=10, graphs_per_row=2)
'''

'''
import pickle

# Save the contact_graph dictionary to a file using pickle
with open('contact_graph.pkl', 'wb') as file:
    pickle.dump(contact_graph, file)

print("Contact graph saved successfully to contact_graph.pkl")
'''

'''
import pickle

# Load the contact_graph dictionary from the saved file
with open('contact_graph.pkl', 'rb') as file:
    loaded_contact_graph = pickle.load(file)

print("Contact graph loaded successfully from contact_graph.pkl")
'''

def change_edge_weights(contact_graph, new_weight):
    """
    Change the weight of all edges in the contact graph to a new specified weight.
   
    """
    for time_bucket, graph in contact_graph.items():
        for u, v, data in graph.edges(data=True):
            data['weight'] = new_weight

# change edge weights
change_edge_weights(contact_graph, P_INF)
print("Edge weights in the contact graph have been updated to", P_INF)



