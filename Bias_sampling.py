# ground truth simulation
def monte_carlo_simulation(contact_graph, all_nodes, initial_infected, P_INF, r):
    total_infections = 0
    
    for _ in range(r):
        infected = set(np.random.choice(list(all_nodes), int(len(all_nodes) * initial_infected), replace=False))
        susceptible = all_nodes - infected
        sum_infected = 0

        for t in sorted(contact_graph.keys()):
            if t not in contact_graph:
                continue
            
            new_infected = set()
            for u in susceptible:
                if u not in contact_graph[t].nodes:
                    continue
                neighbors = set(contact_graph[t].neighbors(u))
                if any(np.random.rand() < P_INF for v in neighbors if v in infected):
                    new_infected.add(u)
            
            if not new_infected:
                break
            infected |= new_infected
            susceptible -= new_infected
            #sum_infected =  len(infected)
            sum_infected += len(new_infected)
        
        total_infections += sum_infected / r
    
    return total_infections + len(infected)
    

# Set up your contact graph, all_nodes set, and other parameters
# Call the function with the required parameters
all_nodes = set(gowalla_data['user_id'])
sampling_ground_expected = monte_carlo_simulation(contact_graph, all_nodes, INITIAL_INFECTED, P_INF, 1000)
print("ground truth number of infections average 1000 runs:", sampling_ground_expected)



def monte_carlo_simulation(contact_graph, all_nodes, initial_infected, P_INF, r, sample_rate):
    total_infections = 0

    node_list = set(np.random.choice(list(all_nodes), int(len(all_nodes) * sample_rate), replace=False))
    for _ in range(r):
        infected = set(np.random.choice(list(node_list), int(len(node_list) * initial_infected), replace=False))
        susceptible = node_list - infected
        sum_infected = 0

        for t in sorted(contact_graph.keys()):
            if t not in contact_graph:
                continue
            
            new_infected = set()
            for u in susceptible:
                if u not in contact_graph[t].nodes:
                    continue
                neighbors = set(contact_graph[t].neighbors(u))
                if any(np.random.rand() < P_INF for v in neighbors if v in infected):
                    new_infected.add(u)
            
            if not new_infected:
                break
            infected |= new_infected
            susceptible -= new_infected
            sum_infected += len(new_infected)
        
        total_infections += sum_infected / r
    
    return (total_infections + len(infected)) / sample_rate

SAMPLING_PROPORTIONS = [0.025, 0.05, 0.1, 0.2]  # Sampling proportions
sampling_expected_infections = []  # Initialize list to store results

for sub_sample_rate in range(len(SAMPLING_PROPORTIONS)):
    sampling_expected_infections.append(monte_carlo_simulation(contact_graph, all_nodes, INITIAL_INFECTED, P_INF, 10000, SAMPLING_PROPORTIONS[sub_sample_rate]))
    print("Sample rate", SAMPLING_PROPORTIONS[sub_sample_rate], "Number of infections average over 10000 runs:", sampling_expected_infections[sub_sample_rate])



# Calculate biases for each sampling proportion
biases = [sampling_ground_expected - sampling_expected_infections[i] for i in range(len(SAMPLING_PROPORTIONS))]

# Plot the bias graph
plt.figure(figsize=(10, 6))
plt.plot(SAMPLING_PROPORTIONS, biases, marker='o', color='b', linestyle='-')
plt.xlabel('Sampling Rate')
plt.ylabel('Bias in Number of Infections')
plt.title('Bias between Sampling Ground Expected and Expected Infections')
plt.grid(True)
plt.show()
