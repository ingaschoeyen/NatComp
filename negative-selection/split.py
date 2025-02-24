import sys
from math import floor

'''
Input: data.in labels.in positive.out negative.out
Given files <data.in> (arbitrary N lines) and <labels.in> (N lines, each "0" or "1")
write line at i-th row to <negative.out> <=> i-th row of <labels.in> contains "0"
(otherwise to <positive.out>).
'''

with open(sys.argv[1]) as data, open(sys.argv[2]) as labels:
    lines = data.readlines()
    labels = labels.readlines()
lines = [line.strip('\n') for line in lines]
labels = [label.strip('\n') for label in labels]

assert (len(lines) == len(labels)) and "Unequal amount of lines"

with open(sys.argv[3], 'w') as positive, open(sys.argv[4], 'w') as negative:
    for i, line in enumerate(lines):
        if labels[i] == "0":
            negative.write(line + "\n")
        elif labels[i] == "1":
            positive.write(line + "\n")
        else:
            assert False and "Unknown label"