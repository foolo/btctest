## Workflow

### Collect r values from third party API

    python3 bitcointest_ecdsa.py $WORK_DIR

Will output $WORK_DIR/r_archive.txt

### Sort

    sort $WORK_DIR/r_archive.txt > $WORK_DIR/r_archive_sorted.txt

### Find duplicate r values

    python3 find_duplicates.py $WORK_DIR/r_archive_sorted.txt > $WORK_DIR/duplicate_r_values.txt

### Collect data from third party API for each duplicate r value

    python3 parse_duplicates.py $WORK_DIR/duplicate_r_values.txt > $WORK_DIR/parsed_duplicates.json
