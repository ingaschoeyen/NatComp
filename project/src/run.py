from plotting import *
from geometry import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_uniform(100, 2)
    cands.init_uniform(10, 2)
    # Plot first past the post for generated population
    plot_closest(voters, cands, "./res_dis.png")
    plot_histogram(closest_points(voters.pop, cands.pop, distance_euclid), "./res_hist.png")
