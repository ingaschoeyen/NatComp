import sys
import numpy as np

data = sys.argv[1]

print("Longest line in file:", max([len(line) for line in open(data)]))
print("Shortest line in file:", min([len(line) for line in open(data)]))
print("Average line length:", np.mean([len(line) for line in open(data)]))
print("Variance of line length:", np.var([len(line) for line in open(data)]))