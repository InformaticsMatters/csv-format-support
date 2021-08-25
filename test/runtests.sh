#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Run all the Tests.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Success test 1.1 - comma separated, header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=1
export DATASET_FILENAME=test1-csv.smi
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
rm -rf -f test/${TEST_TYPE}/${TEST_DIR}/output
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile1-1.csv

# -----------------------------------------------------------------------------
# Success test 1.2 - comma separated, no header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=1
export DATASET_FILENAME=test1-csv-no-heading.smi
export DATASET_EXTRA_VARIABLES='header=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile1-2.csv

# -----------------------------------------------------------------------------
# Success test 2 - tab separated
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=2
export DATASET_FILENAME=test2-tab.smi
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Success test 3.1 - comma separated, uuid exists, header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=3
export DATASET_FILENAME=test3-csv-uuid.smi
export DATASET_EXTRA_VARIABLES='generate_uuid=False'
export DATASET_OUTPUT_FORMAT=
rm -rf -f test/${TEST_TYPE}/${TEST_DIR}/output
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile3-1.csv

# -----------------------------------------------------------------------------
# Success test 3.2 - comma separated, uuid exists, no header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=3
export DATASET_FILENAME=test3-csv-uuid-no-heading.smi
export DATASET_EXTRA_VARIABLES='generate_uuid=False&header=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile3-2.csv

# -----------------------------------------------------------------------------
# Success test 3.3 - comma separated, uuid exists, generate
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=3
export DATASET_FILENAME=test3-csv-uuid.smi
export DATASET_EXTRA_VARIABLES=''
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile3-3.csv
mv test/${TEST_TYPE}/${TEST_DIR}/output/test3-csv-uuid.smi test/${TEST_TYPE}/${TEST_DIR}/output/test3-csv-uuid3-3.smi

# -----------------------------------------------------------------------------
# Success test 3.4 - comma separated, uuid exists, gemerate, no header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=3
export DATASET_FILENAME=test3-csv-uuid-no-heading.smi
export DATASET_EXTRA_VARIABLES='header=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile3-4.csv
mv test/${TEST_TYPE}/${TEST_DIR}/output/test3-csv-uuid-no-heading.smi test/${TEST_TYPE}/${TEST_DIR}/output/test3-csv-uuid-no-heading3-4.smi

# -----------------------------------------------------------------------------
# Success test 4.1 - Process with non-fatal errors: comma separated, invalid smiles, header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=4
export DATASET_FILENAME=test4-csv-smiles-non-fatal-error.smi
export DATASET_EXTRA_VARIABLES=''
export DATASET_OUTPUT_FORMAT=
rm -rf -f test/${TEST_TYPE}/${TEST_DIR}/output
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile4-1.csv

# -----------------------------------------------------------------------------
# Success test 4.2 - Process with non-fatal errors: comma separated, invalid uuid, header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=4
export DATASET_FILENAME=test4-csv-uuid-non-fatal-error.smi
export DATASET_EXTRA_VARIABLES='generate_uuid=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile4-2.csv

# -----------------------------------------------------------------------------
# Success test 4.3 - Process with non-fatal errors: comma separated, invalid uuid, header
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=4
export DATASET_FILENAME=test4-csv-uuid-non-fatal-error.smi
export DATASET_EXTRA_VARIABLES=''
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile4-3.csv

# -----------------------------------------------------------------------------
# Success test 5.1 - comma separated, header, zipped
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=5
export DATASET_FILENAME=test1-csv.smi.gz
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
rm -rf -f test/${TEST_TYPE}/${TEST_DIR}/output
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile1-1.csv

# -----------------------------------------------------------------------------
# Success test 5.2 - comma separated, no header, zipped
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=5
export DATASET_FILENAME=test1-csv-no-heading.smi.gz
export DATASET_EXTRA_VARIABLES='header=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
mv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile.csv test/${TEST_TYPE}/${TEST_DIR}/output/tmploaderfile1-2.csv

# -----------------------------------------------------------------------------
# Success test 6.1 - comma separated, header with annotation file
# -----------------------------------------------------------------------------
export TEST_TYPE=success
export TEST_DIR=6
export DATASET_FILENAME=test1-csv.smi
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
rm -rf -f test/${TEST_TYPE}/${TEST_DIR}/output
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Failure test 1.1 - comma separated - fail due to no smiles column
# -----------------------------------------------------------------------------
export TEST_TYPE=failure
export TEST_DIR=1
export DATASET_FILENAME=test1-csv-fail.smi
export DATASET_EXTRA_VARIABLES=
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up

# -----------------------------------------------------------------------------
# Failure test 1.2 - comma separated - fail due to no smiles column
# -----------------------------------------------------------------------------
export TEST_TYPE=failure
export TEST_DIR=1
export DATASET_FILENAME=test1-csv-fail-no-heading.smi
export DATASET_EXTRA_VARIABLES='header=False'
export DATASET_OUTPUT_FORMAT=
mkdir -p test/${TEST_TYPE}/${TEST_DIR}/output
IMAGE_NAME=${PWD##*/} docker-compose up
