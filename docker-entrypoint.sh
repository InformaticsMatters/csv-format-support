#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# The DataTier Dataset 'format support' container entrypoint.
# -----------------------------------------------------------------------------
# Refer to RULES.md for comprehensive format support rules,
# summarised below...
#
#    Formatting rules
#    ----------------
# 1. The environment variable `DT_DATASET_FILENAME` will be set to
#    a string value representing the filename of the dataset.
#    i.e. 'data.sdf'. The formatters will not be presented with compressed
#    files.
# 2. The environment variable `DT_DATASET_INPUT_PATH` will be
#    a directory you can find the file defined in part 1
# 3. The environment variable `DT_DATASET_OUTPUT_PATH` will be
#    a directory you can write to
# 4. The output path may not be empty, and the image must be aware of this
#    possibility. The container must not remove any files (from the input or
#    or output directory).
# 5. If available, additional format variables will be presented, as text,
#    in the variable `DT_DATASET_EXTRA_VARIABLES`.
#
#    Conversion
#    ----------
#    As well as the above, when called upon to change file formats...
#
# 1. The optional environment variable `DT_DATASET_OUTPUT_FORMAT` will be set
#    if a file format conversion, rather than data loading, is to be performed.
#    This is expected be a MIME type supported by the image
# 2. If `DT_DATASET_OUTPUT_FORMAT` is set, the environment variable
#    `DT_DATASET_OUTPUT_FILENAME` will be set, i.e. 'data.sdf.gz'.
#    The conversion process simply checks whether the filename ends '.gz'
#    to determine whether compression (gzip) is required. The file must be
#    written to the directory specified by `DT_DATASET_OUTPUT_PATH`.
# -----------------------------------------------------------------------------

# Replace this text and the remainder of the file
# with your formatter implementation...

if [ -n "$DT_DATASET_OUTPUT_FORMAT" ]; then
  python source/converter.py
else
  python source/formatter.py
fi
