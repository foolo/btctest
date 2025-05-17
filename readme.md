## Workflow

### Collect r values from third party API

    python3 bitcointest_ecdsa.py $WORK_DIR

Will output $WORK_DIR/r_archive.txt

    r_value_hex, block_id, tx_index, input_index

### Sort

    sort --unique $WORK_DIR/r_archive.txt > $WORK_DIR/r_archive_sorted.txt

### Find duplicate r values

    python3 find_duplicates.py $WORK_DIR/r_archive_sorted.txt > $WORK_DIR/duplicate_r_values.txt

### Collect data from third party API for each duplicate r value

    python3 parse_duplicates.py $WORK_DIR/duplicate_r_values.txt > $WORK_DIR/parsed_duplicates.txt

    => r, s, signature_hash_int, tx_hash, input_index

### Solve pairs

    python3 solve_pairs.py $WORK_DIR/parsed_duplicates.txt > $WORK_DIR/solved_pairs.txt

    => private_key, sig_info1.tx_hash, sig_info1.input_index, sig_info2.tx_hash, sig_info2.input_index

### Check addresses

    python3 check_addresses.py $WORK_DIR/solved_pairs.txt
