import sys
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt





negres_files = sys.argv[1].split()
posres_files = sys.argv[2].split()

fig, ax = plt.subplots()
plt.xlabel("1 - Specificity")
plt.ylabel("Sensitivity")

for i, (negres_file, posres_file) in enumerate(zip(negres_files, posres_files), start=1):
    posvals, negvals, posvals_lab, negvals_lab = [], [], [], []
    
    print("posres_file:", posres_file)  
    print("negres_file:", negres_file)
    with open(posres_file) as posresults, open(negres_file) as negresults:
        for line in posresults:
            posvals_lab.append((float(line), True))
            posvals.append(float(line))
        for line in negresults:
            negvals_lab.append((float(line), False))
            negvals.append(float(line))


    sortedvals = sorted(list(posvals_lab + negvals_lab))

    sensitivity, specificity = [1], [1]

    tp = len(posvals)
    tn = 0
    fp = 0
    fn = len(negvals)
    lastval = -1
    possum = 0
    negsum = 0


    for j, (val, ispos) in enumerate(sortedvals):
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

    auc_score = roc_auc_score([True for _ in range(len(posvals))] + [False for _ in range(len(negvals))], posvals + negvals)
    ax.plot(specificity, sensitivity, label=f"r = {i}, AUC = {round(auc_score, 2)}")

    print("results from r = ", i)
    print("average positive score:", possum / len(posvals))
    print("average negative score:", negsum / len(negvals))
    print("auc:", auc_score)    
ax.plot([0, 1], [0, 1], linestyle='--')
ax.legend()

# plt.show()
plt.savefig(sys.argv[3])