"""Process an input chemistry/smi file and create
1. A smi (csv file with smiles as it's first column)  file containing data to
 load into database
2. An (optionally) rewritten input file containing a uuid identifier
"""
import logging
import os
import traceback
import csv
import sys
import uuid
import datetime
import json
import gzip

from typing import Dict

from standardize_molecule import standardize_to_noniso_smiles
from data_manager_metadata.metadata import (FieldsDescriptorAnnotation,
                                            get_annotation_filename)
from data_manager_metadata.annotation_utils import est_schema_field_type

from rdkit import Chem, RDLogger

# The columns *every* standard file is expected to contain.
# All standard files must start with these columns.
_OUTPUT_COLUMNS = ['smiles', 'inchis', 'inchik', 'hac', 'molecule-uuid',
                   'rec_number']

# Base FieldsDescriptor fields to create an SDF annotation with.
_BASE_FIELD_NAMES = {
    'smiles': {'type': 'string', 'description': 'Smiles',
               'required': True, 'active': True},
    'uuid': {'type': 'string', 'description': 'Unique Identifier',
             'required': True, 'active': True},
    }

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
event_formatter = logging.Formatter\
    ('%(asctime)s # %(levelname)s -EVENT- %(message)s')
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
    _valid_params = ['generate_uuid', 'header']
    process_vars['generate_uuid'] = True
    process_vars['header'] = True

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

        if isinstance(process_vars['header'], str) and \
                process_vars['header'].lower() in ['false']:
            process_vars['header'] = False

        return process_vars

    except:  # pylint: disable=bare-except
        event_logger.error('Problem decoding parameters - please check format')
        sys.exit(1)


def noniso_smiles(smiles: str):
    """"
    Return a non-isometric smiles representation
    If this fails then the file is likely to be rubbish..
    """

    try:
        noniso = standardize_to_noniso_smiles(smiles)
        return noniso
    except:  # pylint: disable=bare-except
        traceback.print_exc()
        event_logger.error('%s Caused a failure in RDKit', smiles)
        sys.exit(1)


def is_valid_uuid(value: str):
    """"
    Checks whether ths given value is a UUID
    """

    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def check_name_in_fields(field, value, fields) -> dict:
    """ check the name in the properties. If the name does not exist
    then add the name and type to the fields dictionary.
    """
    if field not in fields:
        fields[field] = est_schema_field_type(value)
    return fields


def uncompress_file():
    """"
    Uncompress the file into the same location
    Remove .gz from filename
    """
    uncompressed_filename = os.path.splitext(dataset_filename)[0]
    uncompressed_path = os.path.join(dataset_input_path, uncompressed_filename)
    file = open(uncompressed_path, "w")
    with gzip.open(input_filename, 'rt') as input_csv:
        data = input_csv.read()
        file.write(data)
        file.close()

    return uncompressed_path, uncompressed_filename


def compress_file():
    """"
    Recompress the file into the same location
    Remove the uncompressed file
    """
    compressed_path = \
        os.path.join(dataset_output_path, dataset_filename)
    file = gzip.open(compressed_path, "wb")
    with open(output_filename, 'rb') as output_file:
        data = bytearray(output_file.read())
        file.write(data)
        file.close()

    # Tidy up
    os.remove(output_filename)
    os.remove(input_filename)


def check_file_format():
    """Identify delimiter, perform basic file level checks and return column
    headings
    :returns: dialect (incl delimiter), headings, column containing smiles,
    column containing uuid
    """

    with open(input_filename, 'rt') as input_csv:
        sniffer = csv.Sniffer()
        sniffer.preferred = [',', '\t']
        try:
            input_dialect = sniffer.sniff(input_csv.read(1024))
        except:  # pylint: disable=bare-except
            event_logger.error\
                ('Problem with file delimiter - must be a comma or a tab')
            sys.exit(1)

    with open(input_filename, 'rt') as input_csv:
        # Reset file pointer after
        input_reader = csv.DictReader(input_csv, dialect=input_dialect)

        # Normally, the first row should contain headings and these are used
        # in the dictionary for copying from the old to the new file.
        # If headings=False, the headings used in the dictionary will be the
        # first line of data - the file pointer is subsequently reset to the
        # top of the file.
        old_headings = next(input_reader)

        input_cols = iter(old_headings)

        # First column should contain be 'smiles'
        smiles_col = next(input_cols)
        # Second column should be 'uuid' if not generating uuid
        second_col = next(input_cols)

        if processing_vars['header']:
            smiles = old_headings[smiles_col]
            uuid_col = old_headings[second_col]
        else:
            smiles = smiles_col
            uuid_col = second_col

        if not noniso_smiles(smiles)[1]:
            event_logger.error\
                ('Problem with file - First column must be smiles')
            sys.exit(1)

        if not processing_vars['generate_uuid'] \
                and not is_valid_uuid(uuid_col):
            event_logger.error\
                ('Problem with file - Second column heading must be uuid')
            sys.exit(1)

        if processing_vars['generate_uuid'] \
                and not is_valid_uuid(uuid_col):
            # If generating uuid and second column is not uuid then add uuid
            # to output headings.
            new_headings = [smiles_col, 'uuid', second_col]
            second_col = 'uuid'
            for col in input_cols:
                new_headings.append(col)
        else:
            new_headings = old_headings

    return input_dialect, old_headings, new_headings, smiles_col, second_col


def _log_progress(num_processed):

    if not num_processed % 50000:
        event_logger.info('%s records processed', num_processed)


def write_output_csv_fail(csv_rewriter, input_row, uuid_col):
    """Still write the given record to the output file in the case of a smiles
    standardisation failure. No uuid is generated in this case.
    :param csv_rewriter: Dict Object
    :param input_row:
    :param uuid_col:
    :returns: uuid for insert into file.
    """

    output_row = dict.fromkeys(output_headings, 0)
    for col in input_row:
        output_row[col] = input_row[col]
    output_row[uuid_col] = ''
    csv_rewriter.writerow(output_row)


def write_output_csv(csv_rewriter, input_row, uuid_col, fields):
    """Write the given record to the output smi file with a generated uuid
    :param csv_rewriter: Dict Object
    :param input_row:
    :param uuid_col:
    :param fields:
    :returns: uuid for insert into file, fields for the Fields Descriptor
    """

    molecule_uuid = str(uuid.uuid4())
    output_row = dict.fromkeys(output_headings, 0)

    # The other columns will be identical to the input.
    for col in input_row:
        output_row[col] = input_row[col]
        # Save any new fields found in list to create Fields descriptor
        fields = check_name_in_fields(col, input_row[col], fields)

    output_row[uuid_col] = molecule_uuid

    # Write the standardised data to the tmploadercsv file
    csv_rewriter.writerow(output_row)

    return molecule_uuid, fields


def process_file(output_writer, input_reader, output_csv_file,
                 output_csv_headings, smiles_col, uuid_col):
    """Process the given dataset and process the molecule
    information, writing it as csv-separated fields to the output.

    As we load the molecule we 'standardise' the SMILES and
    add inchi information.

    :param output_writer: DictWriter instance of csv output file
    :param input_reader: DictReader instance of input csv to process
    :param output_csv_file: SMI File to re-write if adding uuid
    :param output_csv_headings: SMI File headings
    :param smiles_col: the column in the input file that is the smiles.
    :param uuid_col: the column in the input/output file that is the uuid.
    :returns: The number of items processed and the number of failures
    """

    num_processed = 0
    num_failed = 0
    num_mols = 0

    # Note, if there are no headings then the code can't find the smiles and
    # uuid to put in the FieldsDescriptor
    fields = {smiles_col : 'string', uuid_col: 'string'}

    # Jump the first line if there is a header
    if processing_vars['header']:
        next(input_reader)

    # This line is here to avoid a lint warning
    csv_rewriter = object()
    if processing_vars['generate_uuid']:
        # Open smi file if (re)generating uuid column
        csv_rewriter = csv.DictWriter(output_csv_file,
                                      fieldnames=output_csv_headings,
                                      dialect=dialect)
        if processing_vars['header']:
            csv_rewriter.writeheader()

    for row in input_reader:
        num_processed += 1
        _log_progress (num_processed)

        # Standardise the smiles and return a standard molecule.
        noniso = noniso_smiles(row[smiles_col])

        if not noniso[1]:
            num_failed += 1
            if processing_vars['generate_uuid']:
                write_output_csv_fail(csv_rewriter, row, uuid_col)
            event_logger.info('Record %s failed to standardize in RDKit',
                              num_processed)
            continue

        num_mols += 1
        if processing_vars['generate_uuid']:
            # If we are generating a UUID for the molecules then we need to
            # rewrite the input record to a new smi file.
            molecule_uuid, fields = write_output_csv(csv_rewriter, row,
                                                     uuid_col, fields)
        else:
            # if we are not generating a UUID then the molecule name must
            # already contain a UUID.
            if is_valid_uuid(row[uuid_col]):
                molecule_uuid = row[uuid_col]
            else:
                num_failed += 1
                if processing_vars['generate_uuid']:
                    write_output_csv_fail(csv_rewriter, row, uuid_col)
                event_logger.info('Record %s did not contain a valid uuid',
                                  num_processed)
                continue

        inchis = Chem.inchi.MolToInchi(noniso[1], '')

        # Write the standardised data to the tmploadercsv file
        output_writer.writerow({'smiles': noniso[0],
                                'inchis': inchis,
                                'inchik': Chem.inchi.InchiToInchiKey(inchis),
                                'hac': noniso[1].GetNumHeavyAtoms(),
                                'molecule-uuid': molecule_uuid,
                                'rec_number': num_processed})

    if processing_vars['generate_uuid']:
        # End and Close the SMI file if there are no more rows in the input
        # file.
        output_csv_file.close()

    return num_processed, num_failed, num_mols, fields


def process_fields_descriptor(fields):
    """ Create the FieldsDescriptor annotation that will be uploaded with the
    dataset.
    If a schema has been included, then the FieldsDescriptor is initialised
    from this and then upserted with the fields present in the file.
    Any fields in the FD that are not in the file are set to inactive
    """
    origin =  'Automatically created from ' + dataset_filename + ' on ' \
              + str(datetime.datetime.utcnow())

    anno_in_desc = ''
    anno_in_fields = {}
    # If a FieldsDescriptor has been generated from an existing file
    # (say it's a new version of an existing file or derived from an
    # existing file), then prime the fields list
    if os.path.isfile(anno_in_filename):
        with open(anno_in_filename, 'rt') as anno_in_file:
            f_desc = json.load(anno_in_file)
            anno_in_desc = f_desc['description']
            anno_in_fields = f_desc['fields']

    if anno_in_fields:
        event_logger.info('Gernerating annotations from existing '
                          'FieldsDescriptor')
    else:
        anno_in_fields=_BASE_FIELD_NAMES
        event_logger.info('Gernerating new FieldsDescriptor')

    fd_new = FieldsDescriptorAnnotation(origin=origin,
                                        description=anno_in_desc,
                                        fields=anno_in_fields)

    # Match old and new fields
    # If field exists in fields and fd_new then ignore
    # If field in fields but not in fd_new then add
    # If field exists in fd_new but not in fields then make inactive.
    existing_fields = fd_new.get_fields()
    for field in fields:
        if field not in existing_fields:
            fd_new.add_field(field, True, fields[field])

    for field in existing_fields:
        if field not in fields:
            fd_new.add_field(field, False)

    # Recreate output and write the list of annotations to it.
    with open(anno_out_filename, "w") as anno_file:
        json.dump(fd_new.to_dict(), anno_file)
    event_logger.info('FieldsDescriptor generated')


if __name__ == '__main__':
    # Say Hello
    basic_logger.info('smi-format-support')

    # Display environment variables
    basic_logger.info('DT_DATASET_FILENAME=%s', dataset_filename)
    basic_logger.info('DT_DATASET_INPUT_PATH=%s', dataset_input_path)
    basic_logger.info('DT_DATASET_OUTPUT_PATH=%s', dataset_output_path)
    basic_logger.info('DT_DATASET_EXTRA_VARIABLES=%s', dataset_extra_variables)

    processing_vars = get_processing_variables()
    basic_logger.info('generate_uuid=%s', processing_vars['generate_uuid'])
    basic_logger.info('header=%s', processing_vars['header'])
    basic_logger.info('SMI Data Loader')

    # Suppress basic RDKit logging...
    RDLogger.logger().setLevel(RDLogger.ERROR)

    basic_logger.info('Checking input file format %s...', dataset_filename)

    # Non-invasive way of allowing gzip files to be sent.
    # If the input file is a gzip, then uncompress for processing
    # Recompress on exit
    input_filename = os.path.join(dataset_input_path, dataset_filename)
    process_filename = dataset_filename
    compress: bool = False
    if dataset_filename.endswith('.gz'):
        compress: bool = True
        input_filename, process_filename = \
            uncompress_file()

    dialect, input_headings, output_headings, input_smiles_col, input_uuid_col\
        = check_file_format()

    loader_filename = os.path.join(dataset_output_path, 'tmploaderfile.csv')
    base_filename = os.path.splitext(process_filename)[0]
    anno_in_filename = os.path.join(
        dataset_input_path,
        get_annotation_filename(base_filename))
    anno_out_filename = os.path.join(
        dataset_output_path,
        get_annotation_filename(base_filename))

    basic_logger.info('Writing data to %s...', loader_filename)
    basic_logger.info('Looking for current annotation in %s...',
                      anno_in_filename)
    basic_logger.info('Writing annotations to %s...', anno_out_filename)

    # Open the file we'll write the standardised data set to.
    with open(loader_filename, 'wt') as csvfile:
        event_logger.info('Processing %s...', input_filename)
        reader = csv.DictReader(open(input_filename, 'rt'), dialect=dialect,
                                fieldnames=input_headings)
        writer = csv.DictWriter(csvfile, fieldnames=_OUTPUT_COLUMNS)
        writer.writeheader()

        output_csv: object = None
        if processing_vars['generate_uuid']:
            output_filename = \
                os.path.join(dataset_output_path, process_filename)
            output_csv = open(output_filename, 'wt')

        processed, failed, mols, file_fields =\
            process_file(writer, reader, output_csv,
                         output_headings, input_smiles_col,
                         input_uuid_col)

    if compress:
        compress_file()

    process_fields_descriptor(file_fields)

    # Summary
    event_logger.info('{:,} processed molecules'.format(processed))
    basic_logger.info('{:,} molecule failures'.format(failed))
    basic_logger.info('{:,} molecule added'.format(mols))
    basic_logger.info('Process complete')
