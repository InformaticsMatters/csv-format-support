"""Process an input chemistry/csv file and create
1. A csv file containing data to load into database
2. An (optionally) rewritten input file containing a uuid identifier
"""
import logging
import os
import traceback
import csv
import sys
import uuid

from typing import Dict

from rdkit import Chem, RDLogger
from standardize_molecule import standardize_to_noniso_smiles

# The columns *every* standard file is expected to contain.
# All standard files must start with these columns.
_OUTPUT_COLUMNS = ['smiles', 'inchis', 'inchik', 'hac', 'molecule-uuid', 'rec_number']

# Two loggers - one for basic logging, one for events.
basic_logger = logging.getLogger('basic')
basic_logger.setLevel(logging.INFO)
basic_handler = logging.StreamHandler()
basic_formatter = logging.Formatter('%(asctime)s # %(levelname)s %(message)s')
basic_handler.setFormatter(basic_formatter)
basic_logger.addHandler(basic_handler)

event_logger = logging.getLogger('event')
event_logger.setLevel(logging.INFO)
event_handler = logging.StreamHandler()
event_formatter = logging.Formatter('%(asctime)s # %(levelname)s -EVENT- %(message)s')
event_handler.setFormatter(event_formatter)
event_logger.addHandler(event_handler)

# Get and display the environment material
# (guaranteed to be provided)
# using the basic (non-event) logger
dataset_filename = os.getenv('DT_DATASET_FILENAME')
dataset_input_path = os.getenv('DT_DATASET_INPUT_PATH')
dataset_output_path = os.getenv('DT_DATASET_OUTPUT_PATH')
dataset_extra_variables = os.getenv('DT_DATASET_EXTRA_VARIABLES')
processing_vars: Dict = {}


def get_processing_variables():
    """Validate and return extra variables provided by user in API call
    The assumption is that this will be a text block of format name=value
    separated by '&'.

    :returns: process_vars - dictionary of processing variables.
    """
    process_vars = {}

    # Set defaults
    _valid_params = ['generate_uuid']
    process_vars['generate_uuid'] = True

    if not dataset_extra_variables:
        return process_vars

    # Split into list of pairs
    try:
        params = dataset_extra_variables.split('&')
        for row in params:
            param = row.split('=')
            if param[0].lower() in _valid_params:
                process_vars[param[0]] = param[1]

        if isinstance(process_vars['generate_uuid'], str) and \
                process_vars['generate_uuid'].lower() in ['false']:
            process_vars['generate_uuid'] = False

        return process_vars

    except:  # pylint: disable=bare-except
        event_logger.info('Problem decoding parameters - please check format')
        sys.exit(1)


def check_file_format():
    """Validate file header line, identify delimiter and return column headings
    :returns: dialect (incl delimiter), headings, column containing smiles
    """

    with open(input_filename, 'rt') as input_csv:
        sniffer = csv.Sniffer()
        sniffer.preferred = [';', '\t']
        try:
            input_dialect = sniffer.sniff(input_csv.read(1024))
        except:  # pylint: disable=bare-except
            event_logger.info('Problem with file delimiter - must be a comma or a tab')
            sys.exit(1)

    with open(input_filename, 'rt') as input_csv:
        # Reset file pointer after
        input_reader = csv.DictReader(input_csv, dialect=input_dialect)

        # First row should contain headings
        input_headings = next(input_reader)

        # First column should contain be 'smiles'
        input_cols = iter(input_headings)
        smiles_col = next(input_cols)

        if smiles_col.lower() != 'smiles':
            event_logger.info('Problem with file - first column heading must be smiles')
            sys.exit(1)

        # Second column should be 'uuid' if not generating uuid
        second_col = next(input_cols)
        if not processing_vars['generate_uuid'] and second_col != 'uuid':
            event_logger.info('Problem with file - second column heading must be uuid')
            sys.exit(1)

        if processing_vars['generate_uuid'] and second_col != 'uuid':
            # If generating uuid and second column is not uuid then add to output headings.
            new_headings = [smiles_col, 'uuid', second_col]
            for col in input_cols:
                new_headings.append(col)
        else:
            new_headings = input_headings

    return input_dialect, new_headings, smiles_col


def is_valid_uuid(value: str):
    """"
    Checks whether ths given value is a UUID
    """

    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def write_output_csv(csv_rewriter, input_row):
    """Write the given record to the output file

    Some of this may end up in std_utils..

    :param csv_rewriter: Dict Object
    :param input_row:
    :returns: uuid for insert into file.
    """

    molecule_uuid = str(uuid.uuid4())
    output_row = dict.fromkeys(output_headings, 0)

    # The other columns will be identical to the input.
    for col in input_row:
        output_row[col] = input_row[col]
    output_row['uuid'] = molecule_uuid

    # Write the standardised data to the tmploadercsv file
    csv_rewriter.writerow(output_row)

    return molecule_uuid


def process_file(output_writer, input_reader, output_csv_file, output_csv_headings, smiles_col):
    """Process the given dataset and process the molecule
    information, writing it as csv-separated fields to the output.

    As we load the molecule we 'standardise' the SMILES and
    add inchi information.

    :param output_writer: DictWriter instance of csv output file
    :param input_reader: DictReader instance of input csv to process
    :param output_csv_file: CSV File to re-write if adding uuid
    :param output_csv_headings: CSV File headings
    :param smiles_col: the column in the input file that is the smiles.
    :returns: The number of items processed and the number of failures
    """

    num_processed = 0
    num_failed = 0
    num_mols = 0

    # csv_rewriter: object = None

    if processing_vars['generate_uuid']:
        # End and Close the SDF file if there are no more molecules.
        csv_rewriter = csv.DictWriter(output_csv_file, fieldnames=output_csv_headings,
                                      dialect=dialect)
        csv_rewriter.writeheader()

    for row in input_reader:
        # If something exists in the molecule_block, then a record has been found,
        # otherwise end of file has been reached.
        num_processed += 1

        try:
            # Standardise the smiles and return a standard molecule.
            noniso = standardize_to_noniso_smiles(row[smiles_col])

            if not noniso[1]:
                num_failed += 1
                event_logger.info('Record %s failed to standardize in RDKit', num_processed)
                continue

            num_mols += 1
            if processing_vars['generate_uuid']:
                # If we are generating a UUID for the molecules then we need to rewrite
                # the input record to a new csv file.
                molecule_uuid = write_output_csv(csv_rewriter, row)
            else:
                # if we are not generating a UUID then the molecule name must already contain
                # a UUID.
                if is_valid_uuid(row['uuid']):
                    molecule_uuid = row['uuid']
                else:
                    num_failed += 1
                    event_logger.info('Record %s did not contain a valid uuid', num_processed)
                    continue

            inchis = Chem.inchi.MolToInchi(noniso[1], '')
            inchik = Chem.inchi.InchiToInchiKey(inchis)

            # Write the standardised data to the tmploadercsv file
            output_writer.writerow({'smiles': noniso[0],
                                    'inchis': inchis, 'inchik': inchik,
                                    'hac': noniso[1].GetNumHeavyAtoms(),
                                    'molecule-uuid': molecule_uuid,
                                    'rec_number': num_processed})

        except:  # pylint: disable=bare-except
            num_failed += 1
            traceback.print_exc()
            event_logger.info('%s Caused a failure in RDKit', row[smiles_col])
            sys.exit(1)

    if processing_vars['generate_uuid']:
        # End and Close the CSV file if there are no more rows in the input file.
        output_csv_file.close()

    return num_processed, num_failed, num_mols


if __name__ == '__main__':
    # Say Hello
    basic_logger.info('csv-format-support')

    # Display environment variables
    basic_logger.info('DT_DATASET_FILENAME=%s', dataset_filename)
    basic_logger.info('DT_DATASET_INPUT_PATH=%s', dataset_input_path)
    basic_logger.info('DT_DATASET_OUTPUT_PATH=%s', dataset_output_path)
    basic_logger.info('DT_DATASET_EXTRA_VARIABLES=%s', dataset_extra_variables)

    processing_vars = get_processing_variables()
    basic_logger.info('generate_uuid=%s', processing_vars['generate_uuid'])
    basic_logger.info('CSV Data Loader')

    # Suppress basic RDKit logging...
    RDLogger.logger().setLevel(RDLogger.ERROR)

    basic_logger.info('Checking input file format %s...', dataset_filename)
    input_filename = os.path.join(dataset_input_path, dataset_filename)
    dialect, output_headings, input_smiles_col = check_file_format()

    # Open the file we'll write the standardised data set to.
    loader_filename = os.path.join(dataset_output_path, 'tmploaderfile.csv')
    basic_logger.info('Writing to %s...', loader_filename)

    with open(loader_filename, 'wt') as csvfile:
        event_logger.info('Processing %s...', input_filename)
        reader = csv.DictReader(open(input_filename, 'rt'), dialect=dialect)
        writer = csv.DictWriter(csvfile, fieldnames=_OUTPUT_COLUMNS)
        writer.writeheader()

        output_csv: object = None
        if processing_vars['generate_uuid']:
            output_filename = os.path.join(dataset_output_path, dataset_filename)
            output_csv = open(output_filename, 'wt')

        processed, failed, mols =\
            process_file(writer, reader, output_csv, output_headings, input_smiles_col)

    # Summary
    event_logger.info('{:,} processed molecules'.format(processed))
    basic_logger.info('{:,} molecule failures'.format(failed))
    basic_logger.info('{:,} molecule added'.format(mols))
    basic_logger.info('Process complete')
