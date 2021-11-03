#!/bin/bash

python -u manage.py ingest \
    --genes ./test_data/genes_test.csv \
    --variants  ./test_data/concatenated_snps_star_test.csv \
    --drugs ./test_data/drugs_test.csv
