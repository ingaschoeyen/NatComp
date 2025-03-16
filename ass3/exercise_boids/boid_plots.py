import sys
import json
import matplotlib.pyplot as plt
import numpy as np

sim_id = sys.argv[1]

# Load data from stdin
data = json.load(sys.stdin)
all_angles = [angle for timestep in data for angle in timestep]

# Create plot
plt.figure(figsize=(10, 6))
plt.hist(all_angles, bins=360, range=(0, 360), density=True)
plt.xlabel('Direction (degrees)')
plt.ylabel('Frequency')
plt.title('Particle Direction Distribution')
plt.grid(True)
plt.savefig('plots/'+sim_id+'output.png')
plt.close()

# create order plot with mean and std shaded in
plt.figure(figsize=(10, 6))
plt.plot(np.mean(all_angles))
plt.fill_between(range(len(all_angles)), np.mean(all_angles) - np.std(all_angles), np.mean(all_angles) + np.std(all_angles), alpha=0.2)
plt.xlabel('Time step')
plt.ylabel('Standard deviation')
plt.title('Standard deviation of particle direction over time')
plt.grid(True)
plt.savefig('plots/'+sim_id+'output_order.png')
plt.close()

# create order plot

