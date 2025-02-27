import sys
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

# sys args: score.pos score.neg figurepath.out

posvals, negvals, posvals_lab, negvals_lab = [], [], [], []

with open(sys.argv[1]) as posresults, open(sys.argv[2]) as negresults:
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

fig, ax = plt.subplots()
plt.xlabel("1 - Specificity")
plt.ylabel("Sensitivity")
ax.plot(specificity, sensitivity)
ax.plot([0, 1], [0, 1], linestyle='--')
auc_score = roc_auc_score([True for _ in range(len(posvals))] + [False for _ in range(len(negvals))], posvals + negvals)
ax.text(0.5, 0.5, 'AOC: ' + str(round(auc_score, 2)))
print("average positive score:", possum / len(posvals))
print("average negative score:", negsum / len(negvals))
print("auc:", auc_score)
# plt.show()
plt.savefig(sys.argv[3])
