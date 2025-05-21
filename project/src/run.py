from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_uniform(1000)
    cands.init_uniform(10)

    # First past the post
    results = fptp(voters, cands)
    plot_closest(voters, cands, output_path="./vis_dis.png")
    # plot_pie(results, output_path="./res_pie_fptp")
    plot_bar(results, output_path="./res_bar_fptp")
    print("ftpt VSE:", vse(voters, cands, results))

    threshold = 0.5
    results = approval_best(voters, cands, threshold)
    # plot_approved(voters, cands, threshold, radius_closest, "./vis_app_closest.png")
    # plot_pie(results, output_path="./res_pie_app_closest")
    plot_bar(results, output_path="./res_bar_app_closest")
    print("Approval best VSE:", vse(voters, cands, results))
    results = approval_worst(voters, cands, threshold)
    # plot_approved(voters, cands, threshold, radius_furthest, "./vis_app_furthest.png")
    # plot_pie(results, output_path="./res_pie_app_furthest")
    plot_bar(results, output_path="./res_bar_app_furthest")
    print("Approval worst VSE:", vse(voters, cands, results))
    results = approval_between(voters, cands, threshold)
    # plot_approved(voters, cands, threshold, radius_between, "./vis_app_between.png")
    # plot_pie(results, output_path="./res_pie_app_between")
    plot_bar(results, output_path="./res_bar_app_between")
    print("Approval between VSE:", vse(voters, cands, results))

    inst_run_thres = 0.1
    results = instant_runoff(voters, cands, threshold=inst_run_thres)
    # plot_pie(results, output_path="./res_pie_instant")
    plot_bar(results, output_path="./res_bar_instant")
    print("Instanf runoff VSE:", vse(voters, cands, results))

    # TODO plot how instant runoff eliminates candidates and counts votes

    candidates = cands.copy()
    round = 0
    shifts = [0 for _ in range(candidates.size())]
    results = fptp(voters, candidates, distance_euclid)
    worst_cand = np.argmin(results)
    plot_closest(voters, candidates, output_path="./" + str(round) + "vis_dis.png")
    plot_bar(results, output_path="./" + str(round) + "res_dis.png")
    print("Instanf runoff round", round, "VSE:", vse(voters, candidates, results))
    while results[worst_cand] / voters.size() <= inst_run_thres:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        results = fptp(voters, candidates, distance_euclid)
        worst_cand = np.argmin(results)
        round += 1

        plot_closest(voters, candidates, shifts, output_path="./" + str(round) + "vis_dis.png")
        # plot_pie(results, output_path="./res_pie_fptp")
        plot_bar(results, shifts, output_path="./" + str(round) + "res_dis.png")
        print("Instanf runoff round", round, "VSE:", vse(voters, candidates, results))
