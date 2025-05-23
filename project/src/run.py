from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_normal(1000)
    cands.init_normal(10)


    results = fptp(voters, cands)
    # print(compute_vse(voters, cands, np.argmax(results)))

    # First past the post
    results = fptp(voters, cands)
    plot_closest(voters, cands, output_path="./fptp_vis.png")
    # plot_pie(results, output_path="./res_pie_fptp")
    plot_bar(results, output_path="./fptp_bar")
    print("ftpt VSE:", vse(voters, cands, results))
    print("ftpt VSE2:", vse2(voters, cands, results))
    print("ftpt VSE3:", vse3(voters, cands, results))

    threshold = 0.5
    results = approval_best(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_closest, "./app_closest_vis.png")
    # plot_pie(results, output_path="./res_pie_app_closest")
    plot_bar(results, output_path="./app_closest_bar")
    print("Approval best VSE:", vse(voters, cands, results))
    print("Approval best VSE2:", vse2(voters, cands, results))
    print("Approval best VSE3:", vse3(voters, cands, results))
    results = approval_worst(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_furthest, "./app_furthest_vis.png")
    # plot_pie(results, output_path="./res_pie_app_furthest")
    plot_bar(results, output_path="./app_furthest_bar")
    print("Approval worst VSE:", vse(voters, cands, results))
    print("Approval worst VSE2:", vse2(voters, cands, results))
    print("Approval worst VSE3:", vse3(voters, cands, results))
    results = approval_between(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_between, "./app_between_vis.png")
    # plot_pie(results, output_path="./res_pie_app_between")
    plot_bar(results, output_path="./app_between_bar")
    print("Approval between VSE:", vse(voters, cands, results))
    print("Approval between VSE2:", vse2(voters, cands, results))
    print("Approval between VSE3:", vse3(voters, cands, results))

    inst_run_thres = 0.1
    results = instant_runoff(voters, cands, threshold=inst_run_thres)
    # plot_pie(results, output_path="./res_pie_instant")
    plot_bar(results, output_path="./inst_bar")
    print("Instanf runoff VSE:", vse(voters, cands, results))
    print("Instanf runoff VSE2:", vse2(voters, cands, results))
    print("Instanf runoff VSE3:", vse3(voters, cands, results))

    # TODO plot how instant runoff eliminates candidates and counts votes

    candidates = cands.copy()
    round = 0
    shifts = [0 for _ in range(candidates.size())]
    results = fptp(voters, candidates, distance_euclid)
    worst_cand = np.argmin(results)
    plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
    # plot_pie(results, output_path="./vse_" + str(round) + "_pie.png"
    plot_bar(results, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
    print("Instanf runoff round", round, "VSE:", vse(voters, candidates, results))
    print("Instanf runoff round", round, "VSE2:", vse2(voters, candidates, results))
    print("Instanf runoff round", round, "VSE3:", vse3(voters, candidates, results))
    while results[worst_cand] / voters.size() <= inst_run_thres:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        results = fptp(voters, candidates, distance_euclid)
        worst_cand = np.argmin(results)
        round += 1

        plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
        # plot_pie(results, output_path="./vse_" + str(round) + "_pie.png"
        plot_bar(results, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
        print("Instanf runoff round", round, "VSE:", vse(voters, candidates, results))
        print("Instanf runoff round", round, "VSE2:", vse2(voters, candidates, results))
        print("Instanf runoff round", round, "VSE3:", vse3(voters, candidates, results))
