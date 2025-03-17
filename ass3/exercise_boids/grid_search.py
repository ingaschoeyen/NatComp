import sys
import matplotlib.pyplot as plt
import numpy as np
import json

# load the output files from boids_out folder and read them 

def read_output_files(sim_id):
    with open('boids_out/'+sim_id+'.json') as f:
        data = json.load(f)
        # extract order parameter
    return data

N = int(sys.argv[1])
max = int(sys.argv[2])



N_fin = np.array((max, max, max))
iter_conv = np.array((max, max, max))

for i in range(max):
    for j in range(max):
        for k in range(max):
            sim_id = 'boids'+str(N)+'_'+str(i)+'_'+str(j)+'_'+str(k)
            data = read_output_files(sim_id)

            if data == None:
                continue

            # plot order parameter and average nearest neighbour distance
            fig = plt.figure()
            fig.plot(len(data['order_parameter']), data['order_parameter'], label='Order parameter')
            fig.plot(len(data['dist_mean']), data['dist_mean'], label='Average Nearest Neighbour Distance')
            plt.fill_between(len(data['dist_mean']), data['dist_mean'] - data['dist_var'], data['dist_mean'] + data['dist_var'], alpha=0.2)
            fig.xlabel('time')
            if data['N'] == 1:
                fig.suptitle('Converged at ' + data['converged'])

            else:
                fig.suptitle('Stopped at ' + str(data['N']) + ' boids')
            fig.title('N='+str(N)+', c='+str(np.floor(i/max))+', s='+str(np.floor(j/max))+', a='+str(np.floor(k/max)))
            fig.savefig('plots/'+sim_id+'.png')
            fig.close()

            # save N and max iter to array
            N_fin[i,j,k] = data['N']
            iter_conv[i,j,k] = data['converged']

# Plot grid search plots
def plot_grid_search(data, title, max):
    """
    Helper function to plot grid search results.
    """
    fig, axs = plt.subplots(int(np.sqrt(max)), int(np.sqrt(max)), figsize=(15, 15))
    fig.suptitle(title, fontsize=16)
    for i in range(max):
        for j in range(max):
            ax = axs[i // int(np.sqrt(max)), i % int(np.sqrt(max))]
            ax.imshow(data[:, :, j], cmap='viridis', origin='lower')
            ax.set_title(f'Parameter k={j}')
            ax.set_xlabel('Parameter i')
            ax.set_ylabel('Parameter j')
    plt.tight_layout()
    return fig

fig = plot_grid_search(N_fin, 'Number of boids at convergence', max)
fig.savefig('plots/N_fin.png')
fig.close()

fig = plot_grid_search(iter_conv, 'Number of iterations at convergence', max)
fig.savefig('plots/iter_conv.png')
fig.close()

