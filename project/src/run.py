from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_uniform(100, 2)
    cands.init_uniform(10, 2)
    # Plot first past the post for generated population
    plot_closest(voters, cands, "./res_dis.png")
    plot_histogram(closest_points(voters.popul, cands.popul, distance_euclid), "./res_hist.png")

    # Debugging
    candidates = cands.copy()
    round = 0
    shifts = [0 for _ in range(candidates.size())]
    results = fptp(voters, candidates, distance_euclid)
    worst_cand = np.argmin(results)
    plot_closest(voters, candidates, "./" + str(round) + "res_dis.png")
    while results[worst_cand] / voters.size() <= 0.1:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        results = fptp(voters, candidates, distance_euclid)
        plot_closest(voters, candidates, "./" + str(round) + "res_dis.png")
        worst_cand = np.argmin(results)
        round += 1
