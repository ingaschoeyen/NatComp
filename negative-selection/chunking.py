import sys

# sys args: data.in n overlap data.out labels.out

n = int(sys.argv[2])
overlap = int(sys.argv[3])

def chunk_sequence(sequence, chunk_size, overlap):
    chunks = [sequence[end - chunk_size : end] for end in range(chunk_size, len(sequence), chunk_size - overlap)]
    left = len(sequence) % (chunk_size - overlap)
    last_chunk = sequence[-left:]
    while len(last_chunk) < chunk_size:
        last_chunk += sequence
    last_chunk = last_chunk[:chunk_size]
    return chunks + [last_chunk]

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