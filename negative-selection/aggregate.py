import sys
import numpy as np

# sys args: scores.in labels scores.out

posvals, negvals, posvals_lab, negvals_lab = [], [], [], []

with open(sys.argv[1]) as scores, open(sys.argv[2]) as labels:
    scores = [float(line.strip('\n')) for line in scores.readlines()]
    labels = [int(line.strip('\n')) for line in labels.readlines()]

line_scores = [[] for _ in range(labels[-1] + 1)]
for i, chunk_score in enumerate(scores):
    line_scores[labels[i]].append(chunk_score)

# Select aggregate function - avg, max, min...
line_score = [sum(x) / len(x) for x in line_scores]
# line_score = [max(x) for x in line_scores]
# line_score = [min(x) for x in line_scores]

with open(sys.argv[3], 'w') as scores_out:
    for score in line_score:
        scores_out.write(str(score) + "\n")
