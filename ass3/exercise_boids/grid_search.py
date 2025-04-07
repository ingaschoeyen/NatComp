import sys
import matplotlib.pyplot as plt
import numpy as np
import json
import os

N = int(sys.argv[1])
max_par = int(sys.argv[2])
inner = int(sys.argv[3])
outer = int(sys.argv[4])


sim_folder = os.path.join(f'sim{N}_{max_par}_{inner}_{outer}/')
if not os.path.exists(sim_folder):
    os.makedirs(sim_folder)

def read_output_files(N, max_par, inner, outer, c, s, a):
    sim_folder = os.path.join('boids_output/' + f'output_{N}_{max_par}_{inner}_{outer}/')
    sim_id = f'output_{c}_{s}_{a}'
    with open(sim_folder+sim_id+'.json') as f:
        data = json.load(f)
        # extract order parameter
    return data

# Plot grid search plots
def plot_grid_search(data, title, max_par):
    """
    Helper function to plot grid search results.
    """
    fig, axs = plt.subplots(int(np.sqrt(max_par)), int(np.sqrt(max_par)), figsize=(15, 15))
    fig.suptitle(title, fontsize=16)
    for i in range(max_par):
        for j in range(max_par):
            ax = axs[i // int(np.sqrt(max_par)), i % int(np.sqrt(max_par))]
            ax.imshow(data[:, :, j], cmap='viridis', origin='lower')
            ax.set_title(f'Parameter k={j}')
            ax.set_xlabel('Parameter i')
            ax.set_ylabel('Parameter j')
    plt.tight_layout()
    return fig



N_fin = np.zeros((max_par, max_par, max_par))
iter_conv = np.zeros((max_par, max_par, max_par))

for i in range(1, max_par + 1):
    for j in range(1, max_par + 1):
        for k in range(1, max_par + 1):
            data = read_output_files(N, max_par, inner, outer, i, j, k)
            sim_id = f'plot_{i}_{j}_{k}'
            if data == None:
                continue
            std_range_up = []
            std_range_down = []
            for l in data['dist_mean']:
                std_range_up.append(l + np.sqrt(data['dist_var'][0]))
                std_range_down.append(l - np.sqrt(data['dist_var'][0]))
            # plot order parameter and average nearest neighbour distance
            plt.figure()
            plt.plot(data['order_parameter'], label='O')
            plt.plot(data['dist_mean'], label=r'$\mathbb{E}[d_{NN}]$')
            plt.plot(std_range_down, std_range_up, alpha=0.2)
            plt.xlabel('time')
            plt.yticks([])
            if data['N'] == 1:
                plt.suptitle('Converged at ' + data['converged'])

            else:
                plt.suptitle('Stopped at ' + str(data['N']) + ' boids')
            plt.title('N='+str(N)+', c='+str(np.round((i/max_par), 2))+', s='+str(np.round((j/max_par), 2))+', a='+str(np.round((k/max_par), 2)))
            plt.legend()
            plt.savefig(sim_folder + '/' +sim_id+'.png')
            plt.close()

            # save N and max_par iter to array
            N_fin[i-1,j-1,k-1] = data['N']
            iter_conv[i-1,j-1,k-1] = data['converged']



fig1 = plot_grid_search(N_fin, 'Number of boids at convergence', max_par)
fig1.savefig(sim_folder + '/' + 'N_fin.png')


fig2 = plot_grid_search(iter_conv, 'Number of iterations at convergence', max_par)
fig2.savefig(sim_folder + '/' + 'iter_conv.png')


