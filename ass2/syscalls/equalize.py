import sys
from math import floor

'''
Input: data.in data.out
Given a file data.in with lines of different length,
padd every line with itself until max length is reached for each line
(truncate last padd so the result is maximum length).
Write output to data.out
'''

max_len = 0
with open(sys.argv[1]) as indata:
    lines = indata.readlines()
lines = [line.strip('\n') for line in lines]

max_len = max([len(line) for line in lines])

transformed = []

for line in lines:
    line_len = len(line)
    padds = floor(max_len / line_len)
    transformed.append((line * padds) + line[:(max_len % line_len)] + '\n')

with open(sys.argv[2], 'w') as outdata:
    for line in transformed:
        assert(len(line) == max_len + 1)
        outdata.write(line)
