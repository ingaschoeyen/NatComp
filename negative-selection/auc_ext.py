import sys
import numpy as np

# sys args: results indices labels out


posvals, negvals, posvals_lab, negvals_lab = [], [], [], []

# sum over lines of same label
line_avg_scores = []

with open(sys.argv[1]) as results, open(sys.argv[2]) as indices, open(sys.argv[3]) as labels, open(sys.argv[4], 'w') as out:
    uniq_indx = np.unique([int(line) for line in indices])
    for indx in uniq_indx:
        mask = (np.array([int(line) for line in indices]) == indx)
        line_avg_scores.append((np.average([float(x) for x in results if mask]), int(labels[indx])))

    # split into positive and negative according to label
    posvals_lab = [float(score) for score, label in line_avg_scores if label == 1]
    negvals_lab = [float(score) for score, label in line_avg_scores if label == 0]

    # sort by score
    sortedvals = sorted(list(posvals_lab + negvals_lab))
