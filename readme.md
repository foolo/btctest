## About

In Bitcoin, ECDSA is used for signing messages (transactions) with the private key.
For each signature, the ECDSA algorithms requires a random number **k** to be generated.
If the same **k** is used in two different signatures, the private key can be calculated.
More details here: https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm#Signature_generation_algorithm

This project is an experiment in which we search the Bitcoin blockchain for duplicate **r** values (**r** is part of the signature, and is derived from **k**, so if the same **k** was used for multiple transactions, we will find duplicate **r** values on the blockchain).

We can then calculate the private key from a pair of signatures (the common **r**, and the unique **s** for both signatures) and the message hash.

## Workflow

### Collect r values from third party API

    python3 bitcointest_ecdsa.py $WORK_DIR

Will output $WORK_DIR/r_archive.txt

### Sort

    sort --unique $WORK_DIR/r_archive.txt > $WORK_DIR/r_archive_sorted.txt

### Find duplicate r values

    python3 find_duplicates.py $WORK_DIR/r_archive_sorted.txt > $WORK_DIR/duplicate_r_values.txt

### Collect data from third party API for each duplicate r value

    python3 parse_duplicates.py $WORK_DIR/duplicate_r_values.txt > $WORK_DIR/parsed_duplicates.txt

### Solve pairs

    python3 solve_pairs.py $WORK_DIR/parsed_duplicates.txt > $WORK_DIR/solved_pairs.txt
