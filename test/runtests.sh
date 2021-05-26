#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Run all the Tests.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Success test 1 - comma separated
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=1
export DATASET_FILENAME=test1-csv.csv
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Success test 2 - tab separated
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=2
export DATASET_FILENAME=test2-tab.csv
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Success test 3 - comma separated, uuid exists
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=3
export DATASET_FILENAME=test3-csv.csv
export DATASET_EXTRA_VARIABLES='generate_uuid=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Failure test 1 - comma separated - fail due to no smiles column
# -----------------------------------------------------------------------------
export TEST_TYPE=failure
export TEST_DIR=1
export DATASET_FILENAME=test1-csv-fail.csv
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
