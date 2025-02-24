import sys
import numpy as np
import matplotlib.pyplot as plt

# sys args: data.in n overlap data.out labels.out

n = int(sys.argv[2])
overlap = int(sys.argv[3])

def chunk_sequence(sequence, chunk_size, overlap):
    chunks = []
    start = 0
    while start + chunk_size <= len(sequence):
        chunks.append(sequence[start : start + chunk_size])
        start += (chunk_size - overlap)
    missing = chunk_size - len(sequence) + start
    chunks.append(sequence[start:] + sequence[:missing])
    return chunks

with open(sys.argv[1], 'r') as data_in, open(sys.argv[4], 'w') as data_out, open(sys.argv[5], 'w') as labels:

    # Read test sequences and labels
    test_sequences = [line.strip() for line in data_in]

    # Process each sequence
    for i, seq in enumerate(test_sequences):
        chunks = chunk_sequence(seq, n, overlap)
        # Write chunks to appropriate files
        for chunk in chunks:
            data_out.write(chunk + '\n')
            labels.write(f'{i} \n')