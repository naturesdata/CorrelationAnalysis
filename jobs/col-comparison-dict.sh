#!/bin/sh

DATA_PATH=$1
COL_TYPES_PATH=$2
TOTAL_N_COLS=$3
SECTION_SIZE=$4
SECTION_IDX=$5
N_CORES=$6
OUT_DIR=$7

python3 col_comparison_dict.py $DATA_PATH $COL_TYPES_PATH $TOTAL_N_COLS $SECTION_SIZE $SECTION_IDX $N_CORES $OUT_DIR