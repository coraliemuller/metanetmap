#!/bin/python
# MISTIC Project INRIA
# Author Muller Coralie
# Date: 2024/11/10
# Update: 2025/08/-

####################################
#      Build database              #
####################################

# Script to create a .tsv file with the UNIQUE-ID of Metacyc database
# and the corresponding informations and ID from other database to do
# the link between them The INCHI have been removed because it seems
# not unique for each metabolite in the database.

# Exemple:
#  UNIQUE-ID	     | CHEBI	|   COMMON-NAME	                                        | ABBREV-NAME |	SYNONYMS	 | ADD-COMPLEMENT  | SEED	  |BIGG	HMDB  |	METANETX	| LIGAND-CPD |	REFMET | PUBCHEM |	CAS |	INCHI-KEY  | SMILES  # noqa: E501
# Teichoic-P-Gro-Glc |	132356	| [(2-Glc)-Gro-P]n-Gro-P-ManNAc-GlcNAc-PP-undecaprenol	|             |[syn1, syn2 ] |		           | cpd28247 |			  | MNXM12982	|			 |	       |	     |      |              | CC(C)=CCCC(\C)=C/CCC(\C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/CCC(/C)=C/COP(=O)([O-])OP([O-])(=O)O[C@@H]1([C@@H]([C@H]([C@@H]([C@H](O1)CO)O[C@@H]3(O[C@H](CO)[C@@H](OP([O-])(=O)OC[C@H](O)COP([O-])(=O)OC[C@H](O[C@H]2(O[C@H](CO)[C@@H](O)[C@H](O)[C@@H](O)2))CO[R])[C@H](O)[C@H](NC(=O)C)3))O)NC(C)=O)  # noqa: E501

import argparse
import csv
import json
import logging
import os
import pandas as pd
import re
import sys
import time
from pathlib import Path

from metanetmap import utils

# set logger
logger = logging.getLogger(__name__)

####################################
#      Utils functions             #
####################################


def split_line(line, column_name, dictionary_temp):
    """Splits a line to extract specific information and adds it to a dictionary.

    Args:
        line (str): A line from the MetaCyc file being read.
        column_name (str): The key under which the extracted
          information will be stored in the dictionary.
        dictionary_temp (dict): The temporary dictionary to update.
    """
    line_name = line.decode("utf-8")  # Convert the binary line to a UTF-8 string
    extract_name = str(line_name).split('"')[1]  # Extract the value between quotes
    dictionary_temp[column_name] = (
        extract_name  # Store the extracted value in the dictionary
    )


def replace_header_line(line, column_name, dictionary_temp):
    """
    Extracts and stores specific information from a header line in the
    MetaCyc file.

    Args:
        line (str): A line from the MetaCyc file being read (in binary format).
        column_name (str): The key under which the extracted
          information will be stored in the dictionary.
        dictionary_temp (dict): The temporary dictionary to update.
    """
    line_name = line.decode("utf-8")  # Convert the binary line to a UTF-8 string
    extract_name = (
        str(line_name).replace(f"{column_name} - ", "").replace("\n", "")
    )  # Clean and extract the value
    dictionary_temp[column_name] = (
        extract_name  # Store the extracted value in the dictionary
    )


def replace_line(line):
    """
    Cleans a line from a MetaCyc file by removing unwanted prefixes, HTML tags,
    and other characters to prepare it for insertion into a dictionary.

    Specifically designed for COMMON-NAME, SYNONYMS, and ABBREV-NAME lines.

    Args:
        line (bytes): The raw line read from the MetaCyc file (in bytes).

    Returns:
        line.strip() (str): Cleaned and simplified string.
    """
    # Decode from bytes to string
    line = line.decode("utf-8")

    # Remove known prefixes
    prefixes = ["COMMON-NAME - ", "SYNONYMS - ", "ABBREV-NAME - "]
    for prefix in prefixes:
        if line.startswith(prefix):
            line = line[len(prefix) :]
            break  # Only one prefix should match

    # Replace common HTML entities and symbols
    replacements = {"&": "", ";": "", "rarr": "->", "\n": "", "a ": "", "an ": ""}
    for old, new in replacements.items():
        line = line.replace(old, new)

    # Remove HTML tags (e.g., <i>, </i>, <sup>, <SUB>, etc.)
    line = re.sub(r"</?(i|I|sup|SUP|sub|SUB)>", "", line)

    return line.strip()



###########################################
#          Main Script Metacyc            #
###########################################


def build_main_dictionary(metacyc_file):
    """
    Builds a main dictionary from a MetaCyc file using the 'UNIQUE-ID'
    as the primary key, and maps various identifiers from other
    databases for each metabolite.

        Exemple of the structure :
        {'UNIQUE-ID': 'CPD-17659', 'CHEBI': '85306', 'COMMON-NAME':
          'D-allo-isoleucine', 'ABBREV-NAME': '', 'SYNONYMS': '',
          'ADD-COMPLEMENT': '', 'SEED': '', 'BIGG': '', 'HMDB': '',
          'METANETX': 'MNXM17053', 'LIGAND-CPD': 'C21092', 'REFMET':
          '', 'PUBCHEM': '6950184', 'CAS': '', 'INCHI-KEY':
          'InChIKey=AGPKZVBTJJNPAG-CRCLSJGQSA-N', 'SMILES':
          'CC[C@H](C)[C@@H]([NH3+])C([O-])=O'}, {...}

    Args:
        metacyc_file (path): Path to the MetaCyc flat file (usually in
          plain-text or .dat format).

    Returns:
        dictionary_db (list of dict): A list of dictionaries, each
          representing one metabolite, with keys for each relevant field.
        keys (list): A list of all the column names/keys used in the
          dictionary, useful for creating a TSV or DataFrame.
    """
    # 1. Try opening and reading the file.
    # Define all possible keys
    keys = [
        "UNIQUE-ID",
        "CHEBI",
        "COMMON-NAME",
        "ABBREV-NAME",
        "SYNONYMS",
        "ADD-COMPLEMENT",
        "MOLECULAR-WEIGHT",
        "MONOISOTOPIC-MW",
        "SEED",
        "BIGG",
        "HMDB",
        "METANETX",
        "LIGAND-CPD",
        "REFMET",
        "PUBCHEM",
        "CAS",
        "INCHI",
        "NON-STANDARD-INCHI",
        "INCHI-KEY",
        "SMILES",
    ]
    optional_fields = keys[1:]  # All except UNIQUE-ID

    dictionary_db = []
    dictionary_temp = {}
    list_synonyms = []

    try:
        with open(metacyc_file, "rb") as file:
            for line in file:

                if b"UNIQUE-ID" in line:
                    # Append previous metabolite before starting new one
                    if dictionary_temp:
                        # Finalize synonyms as string or empty string if none
                        if list_synonyms:
                            dictionary_temp["SYNONYMS"] = list_synonyms
                        else:
                            dictionary_temp["SYNONYMS"] = ""

                        dictionary_db.append(dictionary_temp)
                        dictionary_temp = {}
                        list_synonyms = []

                    # Extract UNIQUE-ID and initialize new dict
                    line_id = line.decode("utf-8").strip()
                    unique_id = line_id.replace("UNIQUE-ID - ", "").strip()
                    dictionary_temp["UNIQUE-ID"] = unique_id

                    # Initialize all optional fields as empty
                    for field in optional_fields:
                        dictionary_temp[field] = ""

                elif b"CHEBI" in line:
                    split_line(line, "CHEBI", dictionary_temp)

                elif b"COMMON-NAME" in line:
                    dictionary_temp["COMMON-NAME"] = replace_line(line)

                elif b"SYNONYMS" in line:
                    synonym = replace_line(line)
                    list_synonyms.append(synonym)

                elif b"ABBREV-NAME" in line:
                    dictionary_temp["ABBREV-NAME"] = replace_line(line)

                elif b"MOLECULAR-WEIGHT" in line:
                    replace_header_line(line, "MOLECULAR-WEIGHT", dictionary_temp)

                elif b"MONOISOTOPIC-MW" in line:
                    replace_header_line(line, "MONOISOTOPIC-MW", dictionary_temp)

                elif b"SEED" in line:
                    split_line(line, "SEED", dictionary_temp)

                elif b"BIGG" in line:
                    split_line(line, "BIGG", dictionary_temp)

                elif b'(HMDB "' in line:
                    split_line(line, "HMDB", dictionary_temp)

                elif b"METANETX " in line:
                    split_line(line, "METANETX", dictionary_temp)

                elif b"LIGAND-CPD " in line:
                    split_line(line, "LIGAND-CPD", dictionary_temp)

                elif b"REFMET " in line:
                    split_line(line, "REFMET", dictionary_temp)

                elif b"PUBCHEM " in line:
                    split_line(line, "PUBCHEM", dictionary_temp)

                elif b"CAS " in line:
                    split_line(line, "CAS", dictionary_temp)

                elif b"INCHI - " in line and b"NON-STANDARD" not in line:
                    replace_header_line(line, "INCHI", dictionary_temp)

                elif b"NON-STANDARD-INCHI - " in line:
                    replace_header_line(line, "NON-STANDARD-INCHI", dictionary_temp)

                elif b"INCHI-KEY - " in line:
                    replace_header_line(line, "INCHI-KEY", dictionary_temp)

                elif b"SMILES" in line:
                    replace_header_line(line, "SMILES", dictionary_temp)

            # After finishing reading the file, append the last metabolite
            if dictionary_temp:
                if list_synonyms:
                    dictionary_temp["SYNONYMS"] = list_synonyms
                else:
                    dictionary_temp["SYNONYMS"] = ""
                dictionary_db.append(dictionary_temp)

        return dictionary_db, keys

    except Exception as e:
        logger.critical(f"Failed to read MetaCyc file '{metacyc_file}': {e}")
        return [], keys


def manage_synonyms(dictionary_db):
    """
    Processes the 'SYNONYMS' field in each dictionary entry by
    converting lists of synonyms into a JSON-formatted string (e.g.,
    '["syn1", "syn2"]') to ensure compatibility with TSV/CSV export.

    Args:
        dictionary_db (list of dict): The main dictionary list
        containing metabolite data, where each entry may have a
        'SYNONYMS' field as a list.

    Returns:
        dictionary_db (list of dict): The updated dictionary list with
        'SYNONYMS' fields converted to JSON strings (if they were lists).
    """
    for dic in dictionary_db:
        for key, value in dic.items():
            if key == "SYNONYMS":
                if isinstance(value, list):
                    s_with_double_quotes = json.dumps(value)
                    dic[key] = s_with_double_quotes

    return dictionary_db



##############################################
#          Add complement                    #
##############################################


def load_database_metanetx(database_conversion):
    """
    Load the database_conversion load_database_metanetx as a dictionary
    to add complement

    Exemple of the structure :
          [{'UNIQUE-ID': 'CPD-17659', 'CHEBI': '85306', 'COMMON-NAME':
          'D-allo-isoleucine', 'ABBREV-NAME': '',
          'SYNONYMS': [], 'ADD-COMPLEMENT': '', 'SEED': '', 'BIGG':
          '', 'HMDB': '', 'METANETX': 'MNXM17053', 'LIGAND-CPD':
          'C21092',
          'REFMET': '', 'PUBCHEM': '6950184', 'CAS': '', 'INCHI-KEY':
          'InChIKey=AGPKZVBTJJNPAG-CRCLSJGQSA-N', 'SMILES':
          'CC[C@H](C)[C@@H]([NH3+])C([O-])=O'},{...}]

    Args:
        database_conversion (path): Path to the database_conversion to
        exhange into dict

    Returns:
        datatable (list): List with all the dictionnaries with
        database_conversion information -> one dic corresponding to
        one row
    """
    datatable = []
    path = Path(database_conversion)

    # Verify that the database_conversion file has been properly loaded
    try:
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                datatable.append(row)
    except Exception as e:
        logger.critical(f"Error reading file: {e}")
        sys.exit(1)
    return datatable

def load_complementary_datatable(datatable_conversion):
    """
    Loads a complementary TSV file where the first column must be
    'UNIQUE-ID'.  All other columns are dynamically extracted and
    stored as individual dictionaries mapping UNIQUE-ID to their
    respective values.

    Args:
        datatable_conversion (str): Path to the complementary TSV file.

    Returns:
        dict[str, dict]: A dictionary of dictionaries, each keyed by
        column name (except 'UNIQUE-ID'), mapping UNIQUE-ID to the
        corresponding value.
          Example:
          {
              'BIGG': {'CPD-123': 'glc', ...},
              'SEED': {'CPD-123': 'cpd00027', ...},
              ...
          }

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If 'UNIQUE-ID' is missing.
        IOError: On read failure.
    """
    if not os.path.isfile(datatable_conversion):
        logger.critical(f"Complementary file not found: {datatable_conversion}")
        raise FileNotFoundError(f"File not found: {datatable_conversion}")

    try:
        with open(datatable_conversion, newline="") as csv_f:
            reader = csv.DictReader(csv_f, delimiter="\t")

            if "UNIQUE-ID" not in reader.fieldnames:
                raise ValueError("Missing 'UNIQUE-ID' column in complementary file.")

            # Initialise a dict of dicts for each column (except UNIQUE-ID)
            column_dicts = {col: {} for col in reader.fieldnames if col != "UNIQUE-ID"}

            for row in reader:
                uid = row["UNIQUE-ID"]
                for col in column_dicts:
                    val = row.get(col, "").strip()
                    if val:  # Ignore empty values
                        column_dicts[col][uid] = val

        logger.info(
            f"Loaded complementary file '{datatable_conversion}' with "
            f"columns: {list(column_dicts.keys())}"
        )
        return column_dicts

    except Exception as e:
        logger.critical(f"Failed to load complementary datatable: {e}")
        raise IOError(f"Error reading complementary file: {e}")


def add_each_complement(dictionary_to_add, column_name_add, dictionary_db):
    """Adds complementary information to a specific column in the main dictionary.

    Args:
        dictionary_to_add (dict): Mapping from UNIQUE-ID to a value
          (for one specific column).
        column_name_add (str): Name of the column to add.
        dictionary_db (list of dict): The main list of metabolite dictionaries.

    Returns:
        dictionary_db(list of dict): Updated dictionary_db with the
          new column added where applicable. If a UNIQUE-ID is in
          dictionary_to_add but not in dictionary_db, a new entry will
          be added.
    """
    # Create a lookup for fast matching
    existing_ids = {d["UNIQUE-ID"]: d for d in dictionary_db if "UNIQUE-ID" in d}

    for uid, value in dictionary_to_add.items():
        if uid in existing_ids:
            existing_ids[uid][column_name_add] = value
        else:
            # Add new entry if UID not found
            dictionary_db.append({"UNIQUE-ID": uid, column_name_add: value})

    return dictionary_db


# /!\ WARNING /!\
# The complementary file need two columns at least:
# -> col1: UNIQUE-ID corresponding to the metabolites id in metacyc
#    file where we want more information,
# -> col2 the column with information to add


# Exemple: UNIQUE-ID | ADD-COMPLEMENT
#   CPD-4211 | N(2)-succinyl-L-arginine
def add_complement_from_complementary(dictionary_db, complementary_dicts):
    """
    Adds all complementary columns from a complementary file to the main dictionary.

    Args:
        dictionary_db (list of dict): Main metabolite list from the MetaCyc file.
        complementary_dicts (dict): Output from load_complementary_datatable(),
                                    with one sub-dictionary per column to add.

    Returns:
        list of dict: The updated dictionary with all complementary columns added.
    """
    for column_name, mapping in complementary_dicts.items():
        dictionary_db = add_each_complement(mapping, column_name, dictionary_db)
    return dictionary_db



###########################################
#          Main Script MetaNetX           #
###########################################



# --- File reading functions ---
def read_chem_prop(path):
    """
    Read the MetaNetX chemical properties file (chem_prop.tsv).

    Parameters
    ----------
    path : str
        Path to the chem_prop.tsv file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing compound properties such as MNX_ID, COMMON_NAME, FORMULA, etc.
    """
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            rows.append({
                "MNX_ID": parts[0] if len(parts) > 0 else "",
                "COMMON_NAME": parts[1] if len(parts) > 1 else "",
                "REFERENCE": parts[2] if len(parts) > 2 else "",
                "FORMULA": parts[3] if len(parts) > 3 else "",
                "CHARGE": parts[4] if len(parts) > 4 else "",
                "MOLECULAR_WEIGHT": parts[5] if len(parts) > 5 else "",
                "INCHI": parts[6] if len(parts) > 6 else "",
                "INCHI_KEY": parts[7] if len(parts) > 7 else "",
                "SMILES": parts[8] if len(parts) > 8 else ""
            })
    return pd.DataFrame(rows)

def read_chem_xref(path):
    """
    Read the MetaNetX cross-reference file (chem_xref.tsv).

    Parameters
    ----------
    path : str
        Path to the chem_xref.tsv file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing cross-reference information between MetaNetX IDs and other databases.
    """
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            rows.append({
                "source": parts[0] if len(parts) > 0 else "",
                "MNX_ID": parts[1] if len(parts) > 1 else "",
                "description": parts[2] if len(parts) > 2 else ""
            })
    return pd.DataFrame(rows)



# --- Extract database-specific IDs ---
def extract_ids(df, db_prefix):
    """
    Extract all external IDs for a given database prefix.

    Parameters
    ----------
    df : pd.DataFrame
        Cross-reference dataframe.
    db_prefix : str
        Prefix identifying the external database (e.g. 'chebi', 'seed', 'hmdb').

    Returns
    -------
    pd.DataFrame
        A dataframe containing MNX_ID and the concatenated list of unique database-specific identifiers.
    """
    subset = df[df["source"].str.startswith(db_prefix)]
    return subset.groupby("MNX_ID")["source"].apply(lambda x: "|".join(sorted(set(x)))).reset_index().rename(columns={"source": db_prefix.upper()})


def explode_ids(df, col):
    """
    Split a '|' separated column into multiple rows.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    col : str
        Column name containing '|' separated values.

    Returns
    -------
    pd.DataFrame
        A new dataframe with one row per unique ID value.
    """
    exploded = []
    for _, row in df.iterrows():
        for val in row[col].split("|"):
            val = val.strip()
            if val:
                exploded.append({**row, col: val})
    return pd.DataFrame(exploded)


def simplify_bigg(val):
    """
    Clean and simplify BiGG metabolite identifiers.

    Removes known prefixes like 'bigg.metabolite:', 'biggM:', or 'M_'.
    """
    if pd.isna(val): return ""
    vals = set()
    for v in val.split("|"):
        v = re.sub(r"^(bigg\.metabolite:|biggM:M_|biggM:|M_)", "", v.strip())
        if v: vals.add(v)
    return "|".join(sorted(vals))


def simplify_seed(val):
    """
    Clean and simplify SEED compound identifiers.

    Removes prefixes such as 'seed.compound:', 'seedM:', and 'M_'.
    """
    if pd.isna(val): return ""
    vals = set()
    for v in val.split("|"):
        v = re.sub(r"^(seed\.compound:|seedM:|M_)", "", v.strip())
        if v: vals.add(v)
    return "|".join(sorted(vals))

def simplify_vmh(val):
    """
    Clean and simplify VMH compound identifiers.

    Removes prefixes such as 'vmhM:', 'vmhM:M_', 'vmhmetabolite:', and 'M_'.
    Ensures that the final identifier is clean (e.g. 'vmhM:M_oh1|vmhM:oh1|vmhmetabolite:oh1' -> 'oh1').
    """
    if pd.isna(val): return ""
    vals = set()
    for v in val.split("|"):
        # Remove all known VMH prefixes
        v = re.sub(r"^(vmhM:M_|vmhM:|vmhmetabolite:|M_)", "", v.strip())
        if v: vals.add(v)
    return "|".join(sorted(vals))

def simplify_hmdb(val):
    """
    Clean and normalize HMDB identifiers.

    If multiple IDs are found, the function keeps the first valid HMDB####### entry.
    """
    if pd.isna(val) or val.strip() == "":
        return ""
    vals = [v.replace("hmdb:", "").strip() for v in val.split("|")]
    valid = [v for v in vals if re.match(r"^HMDB\d{7}$", v)]
    if valid:
        return sorted(valid)[0]
    return sorted(set(vals))[0] if vals else ""


def simplify_metacyc(val):
    """
    Clean and simplify MetaCyc compound identifiers.

    Removes prefixes such as 'metacyc.compound:' and 'metacycM:'.
    """
    if pd.isna(val) or val.strip() == "":
        return ""
    vals = set()
    for v in val.split("|"):
        v = re.sub(r"^(metacyc\.compound:|metacycM:)", "", v.strip())
        if v: vals.add(v)
    return "|".join(sorted(vals))

# --- Final cleanup: remove any remaining 'M_' prefix in SEED and BIGG columns ---
def remove_prefix_M(val):
    """
    Remove the prefix 'M_' from all non-empty cells in a given string.

    Handles multiple IDs separated by '|'.
    """
    if pd.isna(val) or val.strip() == "":
        return val
    vals = [re.sub(r"^M_", "", v.strip()) for v in val.split("|")]
    return "|".join(vals)



######################
#       Run          #
######################


def parse_args():
    """
    Parses command-line arguments for the MetaCyc data conversion script.

    Returns:
        argparse.Namespace: Parsed arguments including:
            - metacyc_file (str): Path to the MetaCyc .dat file
              (default: 'bases/metacyc/compounds_29.dat').
            - complement_file (str): Path to the complementary .tsv
              file (default: 'datatable_complementary.tsv').
            - output (str): Output file name or directory path for the
              resulting TSV (default: 'conversion_datatable.tsv').
            - quiet (bool): If set, runs the script in quiet mode
              (suppress logs except warnings/errors).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--metacyc_file",
        help="Path to the metacyc file for build conversion datatable from Metacyc: .dat",
    )
    parser.add_argument(
        "-r",
        "--chem_ref_file",
        help="Path to the chem_xref file for build conversion datatable from MetaNetX: .tsv",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--chem_prop_file",
        help="Path to the chem_prop file for build conversion datatable from MetaNetX: .tsv",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--complement_file",
        help="Path to the complement file: .tsv",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output filename: .tsv or folder/",
        default="conversion_datatable.tsv",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Output directory name for mapping results",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-x",
        "--metanetx",
        help="Enable the MetaNetX option to build a conversion datatable from the MetaNetX files",
        action="store_true",
    )
        # Quiet mode (less verbose output)
    parser.add_argument(
        "-y",
        "--metacyc",
        help="Enable the Metacyc option to build a conversion datatable from the Metacyc file",
        action="store_true",
    )
    return parser.parse_args()


def load_args(args=None):
    """
    Main function to run the MetaCyc to TSV conversion pipeline.

    Args:
        args (argparse.Namespace, optional): Parsed command-line arguments.
            If None, the arguments will be parsed from sys.argv.

    This function:
        - Parses the MetaCyc .dat file to extract compound information.
        - Optionally loads a complementary file for additional
          identifiers (BIGG, SEED, etc.).
        - Builds the conversion dictionary.
        - Writes the output to a TSV file.
        - Runs in quiet mode if specified (suppresses logs except for warnings/errors).
    """
    if args is None:
        args = parse_args()

    # -------------------------------#
    #       Set up the logger       #
    # -------------------------------#

    t0 = time.time()

    logger.setLevel(logging.DEBUG)

    # ----Clean the root logger (ROOT) ----
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create leveled formatter
    formatter = utils.LeveledFormatter("%(message)s")
    formatter.set_formatter(logging.INFO, logging.Formatter("%(message)s"))
    formatter.set_formatter(
        logging.WARNING,
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )
    formatter.set_formatter(
        logging.CRITICAL,
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )

    # Set up the default console logger
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    if args.quiet:
        console_handler.setLevel(logging.WARNING)
        print("---->    Build database run in quiet mode    <----\n")
    logger.addHandler(console_handler)

    output = Path(args.output)

    # ----------------------------------------#
    #        Check validity of output         #
    # ----------------------------------------#

    # Manage the creation of the output file and directory if they are not
    utils.is_valid_file_or_create(output)
    root, ext = os.path.splitext(output)
    if not ext:  # Check if we have the path for outputfolder but not the name
        # in args, create an arbitrary filename.
        utils.is_valid_dir(root)
        if args.metacyc == True:
            utils.is_valid_file_or_create(f"{root}metacyc_conversion_datatable.tsv")
            output = os.path.join(root, "metacyc_conversion_datatable.tsv")
        elif args.metanetx == True:
            utils.is_valid_file_or_create(f"{root}metanetx_conversion_datatable.tsv")
            output = os.path.join(root, "metanetx_conversion_datatable.tsv")
        else:
            logger.critical(
                "Error: Metacyc and MetanetX option -- only one of them must be selected."
                    )
            sys.exit()
    else:
        stripped = os.path.dirname(output)
        utils.is_valid_dir(stripped)

    

    directory = os.path.dirname(output)
    if directory != "":
        utils.is_valid_dir(f"{directory}/logs/")
        output_log = f"{directory}/logs/"
    else:
        utils.is_valid_dir("logs/")
        output_log = "logs/"

    # #-----------------------------------#
    # #       Set up the logger file      #
    # #------------------------------------#
    # #  # # File handler
    log_file_path = os.path.join(output_log, f"build_database_{t0}.log")
    file_handler = logging.FileHandler(log_file_path, "w+")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ---------------------------------------#
    #      Set up complementary file        #
    # ---------------------------------------#

    logger.info("-----------------------------------------")
    logger.info("            BUILD CONVERTION TABLE ")
    logger.info("----------------------------------------- \n")

    # Check if we have a complementary file : The complementary file
    # allow to add information that are not in the metacyc file.
    complementary_file = args.complement_file

    # ----------------------#
    #    Main command      #
    # ----------------------#

    logger.info("\nCommand run:")
    logger.info("Actual command run (from sys.argv): python " + " ".join(sys.argv))

    if args.metacyc == True:
        utils.is_valid_file(args.metacyc_file)
        if complementary_file:  # iF complementrary file is add
            utils.is_valid_file(complementary_file)

            logger.info("\n---> Run construction of the datatable for Metacyc\n")
            dictionary_db, keys = build_main_dictionary(args.metacyc_file)
            dictionary_db = manage_synonyms(dictionary_db)

            logger.info("---> Complementary file added :")
            column_dicts = load_complementary_datatable(args.complement_file)
            dictionary_db = add_complement_from_complementary(dictionary_db, column_dicts)
            utils.write_csv(dictionary_db, output, keys)
        else:
            logger.info("\n---> Run construction of the datatable for Metacyc")
            logger.info("/!\\  No complementary file added")

            dictionary_db, keys = build_main_dictionary(args.metacyc_file)
            dictionary_db = manage_synonyms(dictionary_db)
            utils.write_csv(dictionary_db, output, keys)
    
    if args.metanetx:

        if complementary_file:  # iF complementrary file is add
            utils.is_valid_file(complementary_file)
    
            logger.info("\n---> Run construction of the datatable for MetaNetX\n")
                        # --- Load data ---
            df_prop = read_chem_prop(args.chem_prop_file)
            df_xref = read_chem_xref(args.chem_ref_file)
            # Extract references for each database
            chebi_df = extract_ids(df_xref, "chebi")
            pubchem_df = extract_ids(df_xref, "pubchem")
            bigg_df = extract_ids(df_xref, "bigg")
            hmdb_df = extract_ids(df_xref, "hmdb")
            refmet_df = extract_ids(df_xref, "refmet")
            seed_df = extract_ids(df_xref, "seed")
            vmh_df = extract_ids(df_xref, "vmh")  

            # --- Extract MetaCyc references ---
            metacyc_df = df_xref[df_xref["source"].str.startswith("metacyc")][["MNX_ID", "source"]].rename(columns={"source": "METACYC"})

            # --- Specific cleaning functions ---
            # CHEBI → one row per ID
            chebi_df = explode_ids(chebi_df, "CHEBI")

            bigg_df["BIGG"] = bigg_df["BIGG"].apply(simplify_bigg)
            bigg_df = explode_ids(bigg_df, "BIGG")
            seed_df["SEED"] = seed_df["SEED"].apply(simplify_seed)
            seed_df = explode_ids(seed_df, "SEED")

            vmh_df["VMH"] = vmh_df["VMH"].apply(simplify_vmh)
            vmh_df = explode_ids(vmh_df, "VMH")

            hmdb_df["HMDB"] = hmdb_df["HMDB"].apply(simplify_hmdb)
            metacyc_df["METACYC"] = metacyc_df["METACYC"].apply(simplify_metacyc)

            # --- Merge all dataframes together ---
            df_final = df_prop.merge(metacyc_df, on="MNX_ID", how="left")
            for d in [chebi_df, pubchem_df, bigg_df, hmdb_df, refmet_df, seed_df, vmh_df]:
                df_final = df_final.merge(d, on="MNX_ID", how="left")

            # Rename MNX_ID → UNIQUE-ID
            df_final = df_final.rename(columns={"MNX_ID": "UNIQUE-ID"})

            # Remove CHARGE column if present
            if "CHARGE" in df_final.columns:
                df_final = df_final.drop(columns=["CHARGE"])

            # Add missing columns if necessary
            for col in ["ABBREV_NAME", "SYNONYMS", "ADD-COMPLEMENT", "NON-STANDARD-INCHI"]:
                if col not in df_final.columns:
                    df_final[col] = ""

            # Reorder columns for final export (added VMH)
            cols_order = [
                "UNIQUE-ID", "CHEBI", "COMMON_NAME", "ABBREV_NAME", "SYNONYMS", "ADD-COMPLEMENT",
                "MOLECULAR_WEIGHT", "SEED", "BIGG", "HMDB", "METACYC",
                "REFMET", "PUBCHEM", "VMH", "CAS", "INCHI", "NON-STANDARD-INCHI", "INCHI_KEY", "SMILES"
            ]
            for c in cols_order:
                if c not in df_final.columns:
                    df_final[c] = ""

            df_final = df_final[cols_order]

            df_final["SEED"] = df_final["SEED"].apply(remove_prefix_M)
            df_final["BIGG"] = df_final["BIGG"].apply(remove_prefix_M)

            # --- Remove full duplicates ---
            df_final = df_final.drop_duplicates()

            # --- Save final merged table ---
            df_final.to_csv(output, sep="\t", index=False)
            logger.info(f"Final merged table generated: {output}")
    
            logger.info("---> Complementary file added :")
            column_dicts = load_complementary_datatable(args.complement_file)
            dictionary_db_metanetx=load_database_metanetx(output)
            dictionary_db = add_complement_from_complementary(dictionary_db_metanetx, column_dicts)
            utils.write_csv(dictionary_db, output, cols_order)

        else:
            logger.info("\n---> Run construction of the datatable for MetaNetX")
            logger.info("/!\\  No complementary file added")
    
            
            # --- Load data ---
            df_prop = read_chem_prop(args.chem_prop_file)
            df_xref = read_chem_xref(args.chem_ref_file)
            # Extract references for each database
            chebi_df = extract_ids(df_xref, "chebi")
            pubchem_df = extract_ids(df_xref, "pubchem")
            bigg_df = extract_ids(df_xref, "bigg")
            hmdb_df = extract_ids(df_xref, "hmdb")
            refmet_df = extract_ids(df_xref, "refmet")
            seed_df = extract_ids(df_xref, "seed")
            vmh_df = extract_ids(df_xref, "vmh")  

            # --- Extract MetaCyc references ---
            metacyc_df = df_xref[df_xref["source"].str.startswith("metacyc")][["MNX_ID", "source"]].rename(columns={"source": "METACYC"})

            # --- Specific cleaning functions ---
            # CHEBI → one row per ID
            chebi_df = explode_ids(chebi_df, "CHEBI")

            bigg_df["BIGG"] = bigg_df["BIGG"].apply(simplify_bigg)
            bigg_df = explode_ids(bigg_df, "BIGG")
            seed_df["SEED"] = seed_df["SEED"].apply(simplify_seed)
            seed_df = explode_ids(seed_df, "SEED")

            vmh_df["VMH"] = vmh_df["VMH"].apply(simplify_vmh)
            vmh_df = explode_ids(vmh_df, "VMH")

            hmdb_df["HMDB"] = hmdb_df["HMDB"].apply(simplify_hmdb)
            metacyc_df["METACYC"] = metacyc_df["METACYC"].apply(simplify_metacyc)

            # --- Merge all dataframes together ---
            df_final = df_prop.merge(metacyc_df, on="MNX_ID", how="left")
            for d in [chebi_df, pubchem_df, bigg_df, hmdb_df, refmet_df, seed_df, vmh_df]:
                df_final = df_final.merge(d, on="MNX_ID", how="left")

            # Rename MNX_ID → UNIQUE-ID
            df_final = df_final.rename(columns={"MNX_ID": "UNIQUE-ID"})

            # Remove CHARGE column if present
            if "CHARGE" in df_final.columns:
                df_final = df_final.drop(columns=["CHARGE"])

            # Add missing columns if necessary
            for col in ["ABBREV_NAME", "SYNONYMS", "ADD-COMPLEMENT", "NON-STANDARD-INCHI"]:
                if col not in df_final.columns:
                    df_final[col] = ""

            # Reorder columns for final export (added VMH)
            cols_order = [
                "UNIQUE-ID", "CHEBI", "COMMON_NAME", "ABBREV_NAME", "SYNONYMS", "ADD-COMPLEMENT",
                "MOLECULAR_WEIGHT", "SEED", "BIGG", "HMDB", "METACYC",
                "REFMET", "PUBCHEM", "VMH", "CAS", "INCHI", "NON-STANDARD-INCHI", "INCHI_KEY", "SMILES"
            ]
            for c in cols_order:
                if c not in df_final.columns:
                    df_final[c] = ""

            df_final = df_final[cols_order]

            df_final["SEED"] = df_final["SEED"].apply(remove_prefix_M)
            df_final["BIGG"] = df_final["BIGG"].apply(remove_prefix_M)

            # --- Remove full duplicates ---
            df_final = df_final.drop_duplicates()

            # --- Save final merged table ---
            df_final.to_csv(output, sep="\t", index=False)
            print(f"Final merged table generated: {output}")

    t1 = time.time()
    if args.quiet:
        print(
            "\n--- Total runtime %.2f seconds ---"
            "\n ---> Construction of the database completed" % (t1 - t0)
        )
        print("")
    else:
        logger.info(
            "\n--- Total runtime %.2f seconds ---"
            "\n ---> Construction of the database completed" % (t1 - t0)
        )


if __name__ == "__main__":
    load_args()
