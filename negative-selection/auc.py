import sys
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import numpy as np

posvals, negvals, posvals_lab, negvals_lab = [], [], [], []



fig, ax = plt.subplots()
plt.xlabel("1 - Specificity")
plt.ylabel("Sensitivity")

for i, args in enumerate(sys.argv[:2:-1]):
    with open(sys.argv[i]) as posresults, open(sys.argv[i+1]) as negresults:
        for line in posresults:
            line = line.strip('\n').split()
            # loop through line, if x is Nan, replace with 0
            line_av = [float(x) if x != 'NaN' else 0 for x in line]
            posvals_lab.append((np.average(line_av), True))
            posvals.append(np.average(line_av))
        for line in negresults:
            line = line.strip('\n').split() 
            line_av = [float(x) if x != 'NaN' else 0 for x in line]
            negvals_lab.append((np.average(line_av), False))
            negvals.append(np.average(line_av))

    sortedvals = sorted(list(posvals_lab + negvals_lab))

    sensitivity, specificity = [1], [1]

    tp = len(posvals)
    tn = 0
    fp = 0
    fn = len(negvals)
    lastval = -1
    possum = 0
    negsum = 0

    for i, (val, ispos) in enumerate(sortedvals):
        if ispos:
            tp -= 1
            fp += 1
            possum += val
        else:
            tn += 1
            fn -= 1
            negsum += val
        if lastval != val:
            sensitivity.append(tp / len(posvals))
            specificity.append(1 - tn / len(negvals))
        else:
            sensitivity[-1] = tp / len(posvals)
            specificity[-1] = 1 - tn / len(negvals)
        lastval = val


    sensitivity.append(0)
    specificity.append(0)
    print("average positive score {i}:", possum / len(posvals))
    print("average negative score {i}:", negsum / len(negvals))
    print("auc {i}:", auc_score)

    ax.plot(specificity, sensitivity, label='ROC curve dataset ' + str(i+1))
    auc_score = roc_auc_score([True for _ in range(len(posvals))] + [False for _ in range(len(negvals))], posvals + negvals)
    ax.text(0.5, 0.5, 'AUC: ' + str(round(auc_score, 2)))
ax.plot([0, 1], [0, 1], linestyle='--')
# plt.show()
plt.savefig(sys.argv[3])