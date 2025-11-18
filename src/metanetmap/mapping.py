#!/bin/python
# MISTIC Project INRIA/INRAE
# Author Muller Coralie
# Date: 2024/11/27
# Update: 2025/08/-

####################################
#            MAPPING               #
####################################

# Script to match metabolites between MAF files and SBML files.
# A conversion table is used to perform the matching. This table is
# based on the MetaCyc/MetaNetX database, and includes corresponding
# information and IDs from other databases to establish links.


import ast
import asyncio
import csv
import itertools
import re
import sys
import time
from pathlib import Path

import cobra
import pandas as pd

from metanetmap import utils

####################################
#          Main Script             #
####################################

logger = utils.get_logger("Mapping")


# ---------------------------------#
#     Load the conversion table   #
# ---------------------------------#


def load_database(database_conversion):
    """
    Load the database_conversion as a dictionary
    /!\\ Special handling is applied to the 'SYNONYMS' column: if it's
    a non-empty string, it is converted from a string representation
    of a list to an actual Python list.

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
                if "SYNONYMS" in row and row["SYNONYMS"]:
                    try:
                        row["SYNONYMS"] = ast.literal_eval(row["SYNONYMS"])
                    except Exception:
                        logger.warning(f"Failed to parse SYNONYMS: {row['SYNONYMS']}")
                        row["SYNONYMS"] = []
                    
                # Format CHEBI
                chebi = row.get("CHEBI")
                if chebi:
                    row["CHEBI"] = f"CHEBI:{chebi}"
                # Format PUBCHEM
                pubchem = row.get("PUBCHEM")
                if pubchem:
                    row["PUBCHEM"] = f"PUBCHEM:{pubchem}"
                datatable.append(row)
    except Exception as e:
        logger.critical(f"Error reading file: {e}")
        sys.exit(1)

    return datatable


# ---------------------------------------------------------------------#
#  Preparation sbml and maf list with informations for the mapping    #
# ---------------------------------------------------------------------#


# Set Paths
def set_list_paths(paths_to_list, list_pathways, ext1, ext2):
    """
    Create a list of file paths from a directory or a single file,
    filtering by extension if provided.

    Args:
        paths_to_list (Path | str): Path to a directory or single file
          containing pathway input files.
        list_pathways (List[str]): List to store valid file paths.
        ext1 (str | None): First allowed file extension (e.g., ".sbml").
        ext2 (str | None): Second allowed file extension (e.g., ".xml").

    Returns:
        list_pathways (List[str]): Updated list containing valid file
        paths.
    """
    paths_to_list = Path(paths_to_list)

    if paths_to_list.is_dir():  # If it's a directory
        for path_file in paths_to_list.iterdir():
            if path_file.is_file():
                if ext1:
                    if path_file.suffix == ext1 or path_file.suffix == ext2:
                        list_pathways.append(str(path_file))
                    else:
                        logger.critical(
                            "/!\\ Problem with extension of the file "
                            f"{path_file}: must be {ext1} or {ext2}"
                        )
                        sys.exit()
                else:
                    list_pathways.append(str(path_file))

    elif paths_to_list.is_file():  # If it's a single file
        if ext1:
            if paths_to_list.suffix == ext1 or paths_to_list.suffix == ext2:
                list_pathways.append(str(paths_to_list))
            else:
                logger.critical(
                    "/!\\ Problem with extension of the file "
                    f"{paths_to_list}: must be {ext1} or {ext2}"
                )
                sys.exit()
        else:
            list_pathways.append(str(paths_to_list))

    else:
        logger.critical(
            f"/!\\ The provided path {paths_to_list} is neither a file nor a directory."
        )
        sys.exit()

    return list_pathways


def manage_id_in_metadata_sbml(annotations, tmp_data):
    """
    Cleans and extracts IDs from the SBML annotations and stores them
    in tmp_data.

    This function processes each key-value pair in the `annotations`
    dictionary:
    - If the value is a list, it removes common database prefixes
      (e.g., "CHEBI:", "META:") from each element.
    - If the value is a single string, it removes the prefixes and
      stores it as a list with one element.

    The cleaned results are stored in the `tmp_data` dictionary under
    the same keys.

    Args:
        annotations (dict): Dictionary of annotations (typically from
          SBML metadata). Keys are database names, values can be strings
          or lists of strings.
        tmp_data (dict): Temporary dictionary where cleaned IDs are
          stored.

    Returns:
        tmp_data (dict): Updated tmp_data with cleaned annotation
        values.
    """
    for key, value in annotations.items():
        # Special case: inchikey must always be a string, not a list
        if key == "inchikey":
            tmp_data[key] = [f"INCHIKEY={str(value).strip()}"]
            continue

        if key == "pubchem.compound":
            tmp_data[key] = [f"PUBCHEM:{str(value).strip()}"]
            continue

        tmp_data[key] = []
        if isinstance(value, list):
            tmp_data[key] = [
                str(i).replace("META:", "") for i in value
            ]
        else:
            value_clean = str(value).replace("META:", "")
            tmp_data[key].append(value_clean)
    return tmp_data


def merge_doublons_metadata_sbml(meta_data_sbml, met_name, tmp_data):
    """
    Merge new annotation data (`tmp_data`) into the main SBML metadata
    dictionary (`meta_data_sbml`), avoiding duplicates.

    For each key in `tmp_data` (e.g., database name), the function
    checks if the corresponding values already exist in
    `meta_data_sbml[met_name]`, and if not, appends them.

    Args:
        meta_data_sbml (dict): Main dictionary of metadata for all
          metabolites. Structure: {metabolite_name: {source_db: [ids]}}
        met_name (str): The metabolite name (key in `meta_data_sbml`)
        to update.
        tmp_data (dict): Temporary dictionary containing new metadata
        to merge.

    Returns:
        meta_data_sbml (dict): Updated `meta_data_sbml` with new
        entries added without duplicates.
    """
    for k, v in tmp_data.items():
        # If meta_data_sbml[met_name] doesn't contain this key k yet, create it with an empty list []
        meta_data_sbml[met_name].setdefault(k, [])
        for i in v:
            # Flatten all values in meta_data_sbml[met_name] and check
            # if `i` already exists.
            if i not in itertools.chain.from_iterable(meta_data_sbml[met_name].values()):
                meta_data_sbml[met_name][k].append(i)
        # Remove duplicates after the loop (more efficient)
        meta_data_sbml[met_name][k] = list(dict.fromkeys(meta_data_sbml[met_name][k]))
    return meta_data_sbml



def extract_metadata_sbml(model, meta_data_sbml):
    """
    Extracts annotations and metadata for each metabolite in an SBML
    model and merges the data into the meta_data_sbml dictionary.

    For each metabolite:
    - Adds its ID and formula
    - Parses annotation fields (CHEBI, HMDB, etc.)
    - Avoids duplicates when merging data

    Args:
        model (Model): The SBML model containing metabolites (from
          COBRApy).
        meta_data_sbml (dict): Dictionary where metadata is collected
          and updated. Structure: {metabolite_name: {annotation_type: [values]}}

    Returns:
        meta_data_sbml (dict): Updated meta_data_sbml with metabolite
        metadata from the SBML model.
    """
    # Load and parse the SBML file
    for m in model.metabolites:
        tmp_data = {}
        annotations = m.annotation
        # Existing entry: update ID and formula
        if m.name in meta_data_sbml.keys():
            if m.id.endswith(']'):
                clean_id=m.id.rsplit("[", 1)[0]
            else:
                clean_id=m.id.rsplit("_", 1)[0]
            meta_data_sbml[m.name]["ID"].append(clean_id)
            if m.formula:
                meta_data_sbml[m.name]["formula"].append(m.formula)
            else:
                tmp_data["formula"] = ""
            # Remove duplicates from ID and formula
            for key in ["ID", "formula"]:
                meta_data_sbml[m.name][key] = list(
                    dict.fromkeys(meta_data_sbml[m.name][key])
                )
            # Extract other metadata and merge
            tmp_data = manage_id_in_metadata_sbml(annotations, tmp_data)
            meta_data_sbml = merge_doublons_metadata_sbml(
                meta_data_sbml, m.name, tmp_data
            )
        else:
            # New entry
            tmp_data = {k: [] for k in annotations.keys()}
            tmp_data["ID"] = [m.id]
            if m.id.endswith(']'):
                tmp_data["ID"].append(m.id.rsplit("[", 1)[0])
            else:
                tmp_data["ID"].append(m.id.rsplit("_", 1)[0])
            if m.formula:
                tmp_data["formula"] = [m.formula]
            else:
                tmp_data["formula"] = ""
            tmp_data = manage_id_in_metadata_sbml(annotations, tmp_data)
            meta_data_sbml[m.name] = tmp_data
    return meta_data_sbml


# SBML
def setup_merge_list_sbml_metabolites(List_SBML_paths):
    """
    Creates a list with all IDs of metabolites in all metabolic
    networks (for the community mode) and a directory with key: name
    of one metabolic networks , value the list of metabolites for this
    metabolic networks.

    Args:
        List_SBML_paths (List): List with paths for metabolic networks
          files

    Returns:
        dic_couple_sbml (dic): Dictionary with:  key-> name of one
          metabolic networks , value -> list of metabolites for this
          sbml
        meta_data_sbml (dict): Updated meta_data_sbml with metabolite
          metadata from the SBML model.
    """
    dic_couple_sbml = {}
    meta_data_sbml_merge = {}
    list_metabolites_id_merge = []

    for path_sbml in List_SBML_paths:
        model = cobra.io.read_sbml_model(path_sbml)

        # Extract and merge metadata from the ALL modelS
        meta_data_sbml_merge = extract_metadata_sbml(model, meta_data_sbml_merge)

        # Extract and merge metadata from ONE UNQUE model
        meta_data_sbml = extract_metadata_sbml(model, {})
        flat_list = [ value for compound in meta_data_sbml.values() for v in compound.values()  for value in v]

        # Remove compartment suffix (e.g., "_c", "_e") from metabolite IDs
        list_metabolites_id=[]

        for m in model.metabolites:
            if m.id.endswith(']'):
                clean_id=m.id.rsplit("[", 1)[0]
            else:
                clean_id=m.id.rsplit("_", 1)[0]
            list_metabolites_id.append(clean_id)

        # Add to global merged list
        list_metabolites_id_merge.append(list_metabolites_id)

        # Store metabolite list for this specific SBML file
        dic_couple_sbml[Path(path_sbml).stem] = list_metabolites_id+flat_list

    # Flatten and deduplicate global list
    list_metabolites_id_merge = list(
        dict.fromkeys(itertools.chain.from_iterable(list_metabolites_id_merge))
    )
    return dic_couple_sbml, meta_data_sbml_merge


# Metabolomic files
def setup_merged_list_maf_metabolites(List_MAF_paths):
    """
    Parses a list of MAF (Metabolite Annotation File) files to extract
    and clean metadata, and merges them into a single dictionary and
    DataFrame for downstream comparison.

    Args:
        List_MAF_paths (List[str]): List of file paths to MAF files
        (TSV format).

    Returns:
        maf_dictionnary_clean (Dict[str, List[str]]): Cleaned
          dictionary with keys as column names and values as unique,
          non-empty data.
        keys (List[str]): Original list of keys expected/allowed in
          MAF files.
        maf_merged_df (pd.DataFrame): Merged and deduplicated
          DataFrame from all input MAF files.
    """
    maf_dictionnary_clean = {}
    df_list = []

    # Prepare the maf dictionnary
    maf_dictionnary = {}
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
        "METACYC",
        "LIGAND-CPD",
        "REFMET",
        "PUBCHEM",
        "VMH",
        "CAS",
        "INCHI",
        "NON-STANDARD-INCHI",
        "INCHI-KEY",
        "SMILES",
        "FORMULA",
    ] 

    # Initialize dictionary with empty lists for each key
    for k in keys:
        maf_dictionnary[k] = []

    # Loop over MAF file paths
    for path_maf in List_MAF_paths:
        try:
            df = pd.read_csv(path_maf, sep="\t", header=0)
        except Exception as e:
            logger.critical(f"/!\\ Failed to read MAF file {path_maf}: {e}")
            sys.exit(1)
        # Read and concatenate all files
        df.columns = df.columns.str.upper()
        df_list.append(df)
        
        ##### Check if at least on column name fit with maf file
        # Convert the column index (which is a pandas.Index object) into a standard Python list
        column_names_check = list(df.columns)
        # Find matches between actual column names and expected names
        matches = set(column_names_check) & set(keys)

        # If there are no matches, raise an error
        if not matches:
            logger.critical( f"None of the expected names match the column names in the file. "
                            f"Check the following allowed column names: {keys}")
            sys.exit(1)


        # Check for tab separation issue (often due to CSV or Excel
        # file saved as wrong format).
        if df.shape[1] == 1:
            logger.critical(
                f"/!\\ The format of '{path_maf}' is not valid. "
                "Make sure it's tab-delimited (TSV)."
            )
            sys.exit(1)

        for col in df.columns:  # Loop on each column of the maf file
            col_upper = col.upper()
            if col_upper in keys:
                df[col] = df[col].astype(str).str.strip()

                # Fix floats formatted as strings with trailing '.0' (e.g., '123456.0' → '123456')
                if col_upper in ["CHEBI", "PUBCHEM"]:
                    df[col] = df[col].apply(
                        lambda x: x[:-2] if isinstance(x, str) and x.endswith(".0") else x
                    )


                # Normalize identifiers for CHEBI column
                if col_upper == "CHEBI":
                    df[col] = df[col].apply(lambda x: (
                        f"CHEBI:{x.split(':', 1)[1].strip()}" if x.lower().startswith("chebi:") else (
                            f"CHEBI:{x}" if x.isdigit() else x
                        )
                    ))

                # Normalize identifiers for PUBCHEM column
                elif col_upper == "PUBCHEM":
                    df[col] = df[col].apply(lambda x: (
                        f"PUBCHEM:{x.split(':', 1)[1].strip()}" if x.lower().startswith("pubchem:") else (
                            f"PUBCHEM:{x}" if x.isdigit() else x
                        )
                    ))
                
                # Normalize identifiers for INCHI-KEY column
                elif col_upper == "INCHI-KEY":
                    df[col] = df[col].apply(lambda x: (
                        f"INCHIKEY={x.split('=', 1)[1].strip()}" if isinstance(x, str) and x.lower().startswith("inchikey=")
                        else f"INCHIKEY={x.strip()}" if isinstance(x, str) and x.strip().lower() not in ["", "nan"]
                        else x
                    ))

                # Common cleaning for all columns
                df[col] = df[col].apply(utils.fix_arrows_in_parentheses) 
                # Add to dictionary
                maf_dictionnary[col_upper].extend(df[col].tolist())  
                # Remove duplicates while preserving order
                maf_dictionnary[col_upper] = list(dict.fromkeys(maf_dictionnary[col_upper]))


    # Remove keys with only empty values (e.g., "", nan)
    maf_dictionnary_clean = utils.remove_empty_keys(maf_dictionnary)
    maf_dictionnary_clean = {
        k: v for k, v in maf_dictionnary_clean.items() if v != ["nan"]
    }

    # Merge all DataFrames and remove duplicates
    merged_df = pd.concat(df_list, ignore_index=True, sort=False)

    # Remove duplicates
    maf_merged_df = merged_df.drop_duplicates()
    maf_merged_df.columns = maf_merged_df.columns.str.upper()
    maf_merged_filtered_df = maf_merged_df[maf_dictionnary_clean.keys()]
    return maf_dictionnary_clean, keys, maf_merged_filtered_df


# --------------------------------------------------------------#
#           Manage to remove enantiomeres and Inchey           #
# --------------------------------------------------------------#


def remove_enantiomer_process(value, enantiomers=["D", "L", "R", "S"]):
    """
    Cleans enantiomer prefixes like alpha-D-, beta-D-, etc., and
    patterns like __L_ from metabolite names, preserving punctuation
    and structure, and skipping CPD identifiers.

    Args:
        value (str): The input metabolite name.
        enantiomers (list): List of enantiomer letters to clean.

    Returns:
        value.strip() (str): Cleaned name.
    """
    # Do not process identifiers
    if "CPD" in value:
        return value

    for e in enantiomers:
        # 1. Remove if at beginning (e.g., 'D-', 'alpha-D-')
        value = re.sub(
            rf"^(\()?((alpha|beta)-)?{e}-", r"\1", value, flags=re.IGNORECASE
        )

        # 2. Remove enantiomer prefixes inside parentheses (keep '(')
        value = re.sub(rf"\(((alpha|beta)-)?{e}-", "(", value, flags=re.IGNORECASE)

        # 3. Remove enantiomer prefixes AFTER commas, e.g., ', alpha-D-LKL' → ', LKL'
        value = re.sub(
            rf"(,\s*)(\()?((alpha|beta)-)?{e}-", r"\1\2", value, flags=re.IGNORECASE
        )

        # 4. Remove enantiomer prefix ONLY if followed by a closing punctuation
        value = re.sub(
            rf"((alpha|beta)-{e})(?=[\]\)\,\}}])", "", value, flags=re.IGNORECASE
        )

        # 5. Remove [alpha-D- → [ ; (beta-L- → ( ; etc.
        value = re.sub(
            rf"(?<=[\[\(\{{])((alpha|beta)-{e}-)", "", value, flags=re.IGNORECASE
        )

        # 6. Replace inner patterns like -alpha-D- or -D- by -
        value = re.sub(rf"-((alpha|beta)-)?{e}-", "-", value, flags=re.IGNORECASE)

        # 7. Fix malformed patterns like alpha--D-glucose
        value = re.sub(rf"((alpha|beta)--){e}-", "", value, flags=re.IGNORECASE)

        # 8. Remove or replace double underscore enantiomer patterns like __D_, __D
        value = re.sub(rf"__{e}(_|$)", r"\1", value, flags=re.IGNORECASE)

    return value.strip()


def remove_enantiomer_and_Inchey_db(dictionary_db):
    """
    Clean a list of dictionaries (e.g., from MetaCyc/MetaNetX) by:
    - Removing enantiomer notation ('D', 'L', 'R', 'S') from selected
      fields.
    - Trimming the InChIKey to its base fragment (first block before
    first '-').

    Args:
        dictionary_db (list of dict): List of dictionaries, each
          representing a metabolite entry.

    Returns:
        dictionary_db (list of dict): The cleaned list of dictionaries
          with modified fields.
    """
    # Columns to process
    keys_to_clean = ["UNIQUE-ID", "COMMON-NAME", "SYNONYMS", "INCHI-KEY"]

    for dico in dictionary_db:
        for key in keys_to_clean:
            value = dico.get(key)

            if not value or value in ["", [], None]:
                continue  # Skip empty values safely

            if key == "INCHI-KEY":
                # Only keep the root part before the first dash
                dico[key] = value.split("-")[0]

            else:
                # Clean enantiomer notation
                if isinstance(value, list):
                    # Clean each item in the list
                    dico[key] = [
                        remove_enantiomer_process(
                            item, enantiomers=["D", "L", "R", "S"]
                        )
                        for item in value
                    ]
                elif isinstance(value, str):
                    dico[key] = remove_enantiomer_process(
                        value, enantiomers=["D", "L", "R", "S"]
                    )

    return dictionary_db


def remove_enantiomer_and_Inchey_metadata(metadata):
    """
    Clean a dictionary of metadata for metabolites by:
    - Removing enantiomer prefixes ('D', 'L', 'R', 'S') from selected
      fields.
    - Standardizing InChIKeys to keep only the base fragment (before
      first '-').

    Args:
        metadata (dict): A dictionary where keys are metabolite names
        and values are sub-dictionaries containing metadata fields
        like 'ID', 'inchikey', 'biocyc'.

    Returns:
        metadata (dict): Updated metadata dictionary with cleaned values.
    """
    # Columns to process
    keys_to_clean = ["ID", "inchikey", "biocyc"]
    for key_meta, value_meta in metadata.items():
        for key in keys_to_clean:
            value = value_meta.get(key)
            if not value or value in ["", [], None]:
                continue  # Skip empty or invalid fields
            else:
                if isinstance(value, list):
                    # Clean each item in the list
                    value_meta[key] = [
                        remove_enantiomer_process(
                            item, enantiomers=["D", "L", "R", "S"]
                        )
                        for item in value
                    ]

    return metadata



# ------------------------------------------------------------#
#            Harmonisation output preparation                #
# ------------------------------------------------------------#


def setup_harmonisation_output(
    dic_tsv_results, keys_starter, unmatch_metabolites_total, keys
):
    """
    Add unmatched metabolites to dic_tsv_results and harmonize the
    output dictionary keys.

    Args:
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        keys_starter (list): List of base keys expected in each dict.
        unmatch_metabolites_total (list): List of metabolites
          unmatched in both databases.
        keys (list): Additional keys used to create 'Match via {key}'
          columns.

    Returns:
        dic_tsv_results (list of dict): updated list with unmatched
          metabolites added.
        keys_reorder (list): list of all keys in harmonized order.
    """
    # Add each metabolites  which unmatch in both database and
    # metaboloc network to the dic_tsv_results and add their
    # specificities (key_reorder).
    for met in unmatch_metabolites_total:
        temps = {key: (met if key == "Metabolites" else "") for key in keys_starter}
        dic_tsv_results.append(temps)

    # For each metabolite in the dic_tsv_results if a column is not in
    # dic_tsv_results, we create one with empty values.
    # Harmonize keys across all dictionaries
    keys_reorder = keys_starter.copy()  # Start with starter keys

    for dic in dic_tsv_results:
        existing_keys = set(dic.keys())

        # Add keys from keys_starter if missing
        for key in keys_starter:
            if key not in existing_keys:
                dic[key] = ""

        # Add 'Match via {key}' columns for keys in keys
        for key_in_keys in keys:
            match_key = f"Match via {key_in_keys}"
            if match_key not in dic:
                dic[match_key] = ""
            if match_key not in keys_reorder:
                keys_reorder.append(match_key)

    # Remove duplicates preserving order
    keys_reorder = list(dict.fromkeys(keys_reorder))
    return dic_tsv_results, keys_reorder


# ----------------------------------------------------#
#             Match Metabolites                      #
# ----------------------------------------------------#


def check_add_unique_id_to_sbml_match(
    sub_dict, met, Match_id, dic_tsv_results, column_name, database_info
):
    """
    Update dic_tsv_results with unique ID matches in the table
    conversion for a given metabolite.

    Args:
        sub_dict (dict): Dictionary with metabolite info from the database.
        met (str): Metabolite name.
        Match_id (dict): Dictionary tracking metabolites and their
          matched UNIQUE-ID.
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        column_name (str): Column name used for matching.
        database_info (list): List storing info about matched
          metabolites for logging.

    Returns:
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        database_info (list): List storing info about matched
          metabolites for logging.

    """
    if met in Match_id:
        sub_results_dic = utils.find_dict_by_metabolite(dic_tsv_results, met)
        if sub_results_dic:
            
            # Check if UNIQUE-ID is already present in any dic_tsv_results entry
            unique_id_exists = any(
                d.get("Match in database") == sub_dict["UNIQUE-ID"]
                for d in dic_tsv_results
            )

            if not unique_id_exists:
                
                # Get the dict where metabolite matches and update 'Match in database'
                test = next(
                    (d for d in dic_tsv_results if d.get("Metabolites") == met), None
                )

                if test and test.get("Match in database", "") == "":
                    sub_results_dic["Match in database"] = sub_dict["UNIQUE-ID"]
                elif test:
                    sub_results_dic["Match in database"] = (
                        f'{sub_dict["UNIQUE-ID"]} _AND_ {test["Match in database"]}'
                    )
                Match_id[met] = sub_dict["UNIQUE-ID"]

                # Store lowercase unique identifiers
                # from sub_dict for database_info logging
                list_value = [
                    str(value).lower() for value in sub_dict.values() if value != ""
                ]
                list_value.append(sub_dict["UNIQUE-ID"])
                database_info.append(list_value)

                logger.info(
                    f'--"{met}" is present in database with the UNIQUE-ID '
                    f'"{sub_dict["UNIQUE-ID"]}" and matches via '
                    f'"{column_name}"'
                )

            else:
                # If UNIQUE-ID already matched elsewhere, handle duplicates
                test = next(
                    (
                        d
                        for d in dic_tsv_results
                        if d.get("Match in database") == sub_dict["UNIQUE-ID"]
                    ),
                    None,
                )
                logger.info(
                    f'--"{sub_results_dic["Metabolites"]}" is a metabolite '
                    f'duplicate of "{test["Metabolites"]}" and matches via '
                    f'"{column_name}"'
                )

                # Merge metabolite names avoiding redundant concatenations
                met_names = set(sub_results_dic["Metabolites"].split(" _AND_ "))
                met_names.add(test["Metabolites"])
                sub_results_dic["Metabolites"] = " _AND_ ".join(sorted(met_names))

                sub_results_dic["Match in database"] = sub_dict["UNIQUE-ID"]
                Match_id[met] = sub_dict["UNIQUE-ID"]

                list_value = [
                    str(value).lower() for value in sub_dict.values() if value != ""
                ]
                list_value.append(sub_dict["UNIQUE-ID"])
                database_info.append(list_value)

                # Merge 'Match in metabolic networks' if exists in test
                if any(d.get("Match in database") for d in dic_tsv_results):
                    if test and test.get("Match in metabolic networks") is not None:
                        existing = sub_results_dic.get(
                            "Match in metabolic networks", []
                        )
                        # Flatten and deduplicate
                        combined = existing + (
                            test["Match in metabolic networks"]
                            if isinstance(test["Match in metabolic networks"], list)
                            else [test["Match in metabolic networks"]]
                        )
                        sub_results_dic["Match in metabolic networks"] = list(
                            set(combined)
                        )

                # Remove duplicate metabolite entry from dic_tsv_results
                dic_tsv_results = [
                    d
                    for d in dic_tsv_results
                    if d.get("Metabolites") != test["Metabolites"]
                ]
    return dic_tsv_results, database_info


def identification_sbml_match_into_db(
    dictionary_db,
    met,
    column_name,
    dic_tsv_results,
    Match_id,
    database_info,
    key_sub,
    partial,
):
    """
    Match metabolites between SBML IDs and database entries, update
    results and matched IDs.

    Args:
        dictionary_db (dict): Dictionary with metabolite info from the
          database.
        met (str): Metabolite name or partial string to search for.
        column_name (str): Column name used for matching (e.g. 'UNIQUE-ID').
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        Match_id (dict): Dictionary to track matched metabolites and
          their UNIQUE-IDs.
        database_info (list): List to store detailed match info for
          logging or output.
        key_sub (str): Key used for partial matching (e.g. metabolite
          short ID).
        partial (bool): If True, perform matching on partial keys;
          else on full metabolite name.

    Returns:
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results.
        Match_id (dict): Dictionary to track matched metabolites and
          their UNIQUE-IDs.
        database_info (list): List to store detailed match info for
          logging or output.
    """
   # Find all database entries that contain the metabolite or partial string
    sub_dict = utils.find_all_entries_with_value(dictionary_db, met)

    # Use different matching keys based on partial flag ---> Partial
    # is for the last step with partial IDs.
    if partial:
        if len(sub_dict) > 1:
            # If multiple matches, iterate over all and add matches using key_sub
            for dic in sub_dict:
                dic_tsv_results, database_info = check_add_unique_id_to_sbml_match(
                    dic, key_sub, Match_id, dic_tsv_results, column_name, database_info
                )

        elif len(sub_dict) == 1:
            dic_tsv_results, database_info = check_add_unique_id_to_sbml_match(
                sub_dict[0],
                key_sub,
                Match_id,
                dic_tsv_results,
                column_name,
                database_info,
            )
    else:
        if len(sub_dict) > 1:
            # If multiple matches, iterate over all and add matches using met
            for dic in sub_dict:
                dic_tsv_results, database_info = check_add_unique_id_to_sbml_match(
                    dic, met, Match_id, dic_tsv_results, column_name, database_info
                )

        elif len(sub_dict) == 1:
            dic_tsv_results, database_info = check_add_unique_id_to_sbml_match(
                sub_dict[0], met, Match_id, dic_tsv_results, column_name, database_info
            )

    return dic_tsv_results, Match_id, database_info


def match_metab_main(
    dic, met, column_name, dic_tsv_results, Match_id, database_info, dic_temp, partial
):
    """
    Perform matching of a metabolite with database entries and update
    results dictionaries.

    Args:
        dic (dict): One entry (metabolite) from the database.
        met (str): Metabolite name from the input data.
        column_name (str): Column used for the matching
          (e.g. 'COMMON-NAME')

        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        Match_id (dict): Dict linking metabolite names to their
          matched UNIQUE-IDs.
        database_info (list): List collecting detailed matching information.
        dic_temp (dict): Temporary dictionary to store new match info.
        partial (bool): Whether the match is a partial match.

    Returns:
        dic_tsv_results (list of dict): List of dictionaries storing
          match/unmatch results for each metabolite.
        database_info (list): List collecting detailed matching information.
        Match_id (dict): Dict linking metabolite names to their
          matched UNIQUE-IDs.

        if partial,
            dic_tsv_results (list of dict): List of dictionaries
              storing match/unmatch results for each metabolite.
            database_info (list): List collecting detailed matching
              information.
            Match_id (dict): Dict linking metabolite names to their
              matched UNIQUE-IDs.
            dic_temp (dict): Temporary dictionary to store new match info.
    """

    list_value = [
        str(value).lower() for value in dic.values() if value != ""
    ]  # Keep differents identifictaion for ONE metabolite

    # --- Case 1: UNIQUE-ID already matched somewhere
    if dic["UNIQUE-ID"] in Match_id.values():
        sub_results_dic = utils.find_all_entries_with_value_tsv(
            dic_tsv_results, dic["UNIQUE-ID"]
        )
        for sub_sub_results_dic in sub_results_dic:
            # Match each metabolite listed in the result dictionary
            metabolites_list = [m.strip() for m in sub_sub_results_dic["Metabolites"].split(" _AND_ ")]
            if met not in metabolites_list:
                logger.info(
                    '--"%s" is a metabolite duplicate of '
                    '"%s" and matches via "%s" ',
                    met,
                    sub_sub_results_dic["Metabolites"].split("_AND_", 2)[0].strip(),
                    column_name,
                )
                sub_sub_results_dic["Metabolites"] += f" _AND_ {met}"
                sub_sub_results_dic[f"Match via {column_name}"] = (
                    "YES"  # Add "YES" to the specific column for
                    # the doublon name which match.
                )
                Match_id[met] = dic["UNIQUE-ID"]

    # --- Case 2: New match or partial duplicate
    else:


        # Subcase 2.1: Already matched but multiple UNIQUE-IDs (partial)
        if met in Match_id.keys() and Match_id[met] != "NO UNIQUE-ID":
            
            if dic_temp:  # For metabolites with partial match AND not match in
                # STEP1 for sbml matching.
                sub_results_dic = utils.find_matching_dict(dic_tsv_results, met)
                logger.info(
                    f'--"{met}" has a partial match. We have several '
                    "UNIQUE-ID identifiers for this metabolite: "
                    f'"{sub_results_dic[f"Match in database"]}" and '
                    f'"{dic["UNIQUE-ID"]}"'
                )
                sub_results_dic["Partial match"] = (
                    f"{sub_results_dic[f'Match in database']} "
                    f"_AND_ {dic['UNIQUE-ID']}"
                )
                sub_results_dic["Match in database"] = (
                    f"{sub_results_dic[f'Match in database']} "
                    f"_AND_ {dic['UNIQUE-ID']}"
                )
                Match_id[str(met).upper()] = dic["UNIQUE-ID"]
                list_value.append(met)
                database_info.append(list_value)
            else:
                # For metabolites with partial match AND match in
                # STEP1 for sbml matching.
                sub_results_dic = utils.find_dict_by_metabolite(dic_tsv_results, met)
                if sub_results_dic:
                    logger.info(
                        f'--"{met}" has a partial match. We have '
                        "several UNIQUE-ID identifiers for this "
                        f'metabolite: "{sub_results_dic[f"Match in database"]}'
                    )
                    sub_results_dic["Partial match"] = (
                        f"{sub_results_dic[f'Match in database']} "
                        f"_AND_ {dic['UNIQUE-ID']}"
                    )

        # Subcase 2.2: Not matched yet at all
        else:
            dic_temp["Metabolites"] = met
            if partial:
                dic_temp["Partial match"] = dic["UNIQUE-ID"]
                dic_temp["Match in database"] = dic["UNIQUE-ID"]
            else:
                dic_temp["Match in database"] = dic["UNIQUE-ID"]
            Match_id[met] = dic["UNIQUE-ID"]
            dic_temp[f"Match via {column_name}"] = "YES"
            list_value.append(met)
            database_info.append(list_value)
            logger.info(
                f'--"{met}" is present in database with the UNIQUE-ID '
                f'"{dic["UNIQUE-ID"]}" and matches via "{column_name}"'
            )

    # # Add to result if new entry was created
    if dic_temp:
        dic_tsv_results.append(dic_temp)

    # Return according to matching type
    if partial:
        return dic_tsv_results, Match_id, database_info, dic_temp
    else:
        return dic_tsv_results, Match_id, database_info


def match_metabo(
    dictionary_db,
    met,
    column_name,
    dic_tsv_results,
    Match_id,
    database_info,
    key_sub,
    dic_temp_db,
    partial,
):
    """
    Match a metabolite (from SBML or MAF) to entries in the reference
    database (MetaCyc/MetaNetX).

    Args:
        dictionary_db (dict): Full MetaCyc/MetaNetX dictionary.
        met (str): Metabolite name to search.
        column_name (str): Column name used for matching (e.g. COMMON-NAME).
        dic_tsv_results (list of dict)): Output results list of dicts.
        Match_id (dict): Mapping of metabolite name -> UNIQUE-ID.
        database_info (list): List of matched metabolite data from the DB.
        key_sub (str): The original query metabolite used in partial
          matching.
        dic_temp_db (dict): Temp dict to collect partial match info.
        partial (bool): Whether to perform partial matching.

    Returns:
        dic_tsv_results (list of dict): Output results list of dicts.
        Match_id (dict): Mapping of metabolite name -> UNIQUE-ID.
        database_info (list): List of matched metabolite data from the DB.
    """
    # Find all database entries that contain the metabolite or partial string
    sub_dict = utils.find_all_entries_with_value(dictionary_db, met)
    # Use different matching keys based on partial flag ---> Partial
    # is for the last step with partial IDs.
    if partial:
        if len(sub_dict) > 1:
            # If multiple matches, iterate over all and add matches using key_sub
            for dic in sub_dict:
                dic_tsv_results, Match_id, database_info, dic_temp_db = (
                    match_metab_main(
                        dic,
                        key_sub,
                        column_name,
                        dic_tsv_results,
                        Match_id,
                        database_info,
                        dic_temp_db,
                        partial=True,
                    )
                )

        elif len(sub_dict) == 1:
            dict_only = sub_dict[0]
            dic_tsv_results, Match_id, database_info, dic_temp_db = match_metab_main(
                dict_only,
                key_sub,
                column_name,
                dic_tsv_results,
                Match_id,
                database_info,
                dic_temp_db,
                partial=True,
            )


        return dic_tsv_results, Match_id, database_info, dic_temp_db

    else:
        dic_temp = {}
        if len(sub_dict) > 1:
            # If multiple matches, iterate over all and add matches using met
            for dic in sub_dict:
                dic_tsv_results, Match_id, database_info = match_metab_main(
                    dic,
                    met,
                    column_name,
                    dic_tsv_results,
                    Match_id,
                    database_info,
                    dic_temp,
                    partial=False,
                )

        elif len(sub_dict) == 1:
            dict_only = sub_dict[0]
            dic_tsv_results, Match_id, database_info = match_metab_main(
                dict_only,
                met,
                column_name,
                dic_tsv_results,
                Match_id,
                database_info,
                dic_temp,
                partial=False,
            )

        return dic_tsv_results, Match_id, database_info


def match_met_sbml(
    met,
    meta_data_sbml,
    dictionary_db,
    dic_tsv_results,
    Match_id,
    dic_couple_sbml,
    doublons,
    choice,
    column_name,
    database_info,
):
    """
    Matches a metabolite name from SBML metadata to identify if it
    exists in the metabolic network. If found, the function adds
    relevant information to result dictionaries and checks database
    matching.

    Args:
        met (str): Metabolite name to search for.
        meta_data_sbml (dict): Metadata extracted from SBML models.
        dic_tsv_results (list): Accumulator for harmonized result
          dictionaries.
        Match_id (dict): Dictionary tracking matched metabolites and
          their IDs.
        dic_couple_sbml (dict): Maps SBML filenames to lists of
          metabolite IDs.
        doublons (list): List of metabolites matched in the SBML to
          detect duplicates.
        choice (str): Either 'community' or 'none', defines the mode
          of matching.
        column_name (str): The name of the column used for matching
          (e.g. 'COMMON-NAME').
        database_info (list): Accumulator for matched values for
          logging or traceability.

    Returns:
        tuple: Updated dic_tsv_results, Match_id, doublons, and
        database_info.
    """
    dic_temp = {}
    temp_list = []

    # Find sub-dictionary that contains the metabolite
    # print(met)
    sub_dict = utils.find_sub_dict_by_nested_value(meta_data_sbml, met)
    # print(met)
    # print(sub_dict)
    # print("")

    if sub_dict:
        if sub_dict["ID"][0].endswith(']'):
            id_unique_sbml = sub_dict["ID"][0].rsplit("[", 1)[0]
            # print(id_unique_sbml)
        else:
            id_unique_sbml = sub_dict["ID"][0].rsplit("_", 1)[0]            

        # COMMUNITY MODE — associate match with SBML filename
        if choice == "community":
            sbml_name = utils.find_key_by_list_value(dic_couple_sbml, id_unique_sbml)
            temp_list.append(sbml_name)
            logger.info(
                f'--"{met}" is present directly in "{sbml_name}" metabolic network '
                f'with the ID "{id_unique_sbml}" via "{column_name}"'
            )
            
            dic_temp["Match in metabolic networks"] = list(set(temp_list))
        else:
            # CLASSIC MODE — only store ID
            dic_temp["Match in metabolic networks"] = [id_unique_sbml]
            logger.info(
                f'--"{met}" is present directly in metabolic network with the ID '
                f'"{id_unique_sbml}" via "{column_name}"'
            )

        # Add to dic_temp regardless the MODE
        dic_temp["Metabolites"] = f"{met} _AND_ {id_unique_sbml}"
        dic_temp[f"Match via {column_name}"] = "YES"
        dic_temp["Match in database"] = ""
        Match_id[met] = "NO UNIQUE-ID"
        doublons.append(met)

        # If we find a match by formula instead of proper ID — log it as partial
        if utils.check_formula_in_dict(sub_dict, met):
            dic_temp["Partial match"] = met
            logger.info(
                f'--""{met}"" has a partial match. We have a formula '
                f'as identifier for this metabolite: "{met}"'
            )

        # Add to result if new entry was created
        if dic_temp:
            dic_tsv_results.append(dic_temp)

        # Try to complete with info from the database
        dic_tsv_results, Match_id, database_info = identification_sbml_match_into_db(
            dictionary_db,
            met,
            column_name,
            dic_tsv_results,
            Match_id,
            database_info,
            key_sub=None,
            partial=False,
        )
    return dic_tsv_results, Match_id, doublons, database_info


def match_db_sbml(
    met,
    meta_data_sbml,
    dic_tsv_results,
    dic_couple_sbml,
    db_list,
    set_list,
    temp_list,
    choice,
):
    """
    Matches a database metabolite identifier to an SBML network and
    updates result records accordingly.

    Args:
        met (str): The metabolite ID or name used to search in SBML metadata.
        meta_data_sbml (dict): Metadata dictionary extracted from SBML models.
        dic_tsv_results (list of dict): List of dictionaries storing matching results.
        dic_couple_sbml (dict): Maps SBML file names to metabolite IDs.
        db_list (list): List of metabolites found in the database to check against.
        set_list (list): Keys used to identify the relevant dictionary
          in dic_tsv_results.
        temp_list (set): Set used to collect matched SBML file names
          (for community mode).
        choice (str): Mode of operation, either 'community' or 'none'.

    Returns:
        dic_tsv_results (list of dict): List of dictionaries storing matching results.
    """
    sub_dict = utils.find_sub_dict_by_nested_value(meta_data_sbml, met) #to update

    if not sub_dict:
        return dic_tsv_results
    
    if sub_dict["ID"][0].endswith(']'):
        id_unique_sbml = sub_dict["ID"][0].rsplit("[", 1)[0]
    else:
        id_unique_sbml = sub_dict["ID"][0].rsplit("_", 1)[0]    

    sub_results_dic = utils.find_matching_dict_all_key(dic_tsv_results, set_list)
    sbml_names = utils.find_keys_with_value_in_dict(dic_couple_sbml, met)

    temp_list.add(tuple(sbml_names))  # Add SBML names as a tuple for hashability


    if not sub_results_dic or "Metabolites" not in sub_results_dic:
        return dic_tsv_results
    # Match each metabolite listed in the result dictionary
    metabolites = [m.strip() for m in sub_results_dic["Metabolites"].split(" _AND_ ")]

    if id_unique_sbml not in metabolites:
        # COMMUNITY MODE — associate match with SBML filename
        if choice == "community":
            if sbml_names:
                logger.info(
                    f'--"{db_list[-1]}" is present in {sbml_names} '
                    f"metabolic network with the corresponding ID "
                    f'"{id_unique_sbml}" via the match ID "{met}"'
                )
                if sub_results_dic["Metabolites"]:
                    sub_results_dic["Metabolites"]= (
                            f'{sub_results_dic["Metabolites"]} _AND_ {id_unique_sbml}'
                        )
                else:
                    sub_results_dic["Metabolites"]= id_unique_sbml
                # Flatten and deduplicate SBML name list
                flat_list = sorted(
                    set(
                        item
                        for group in temp_list
                        for item in (
                            group if isinstance(group, (list, tuple)) else [group]
                        )
                    )
                )
                sub_results_dic["Match in metabolic networks"] = flat_list 
        else:
            # CLASSIC MODE — only store ID
            sub_results_dic["Match in metabolic networks"] = [id_unique_sbml]
            if sub_results_dic["Metabolites"]:
                sub_results_dic["Metabolites"]= (
                        f'{sub_results_dic["Metabolites"]} _AND_ {id_unique_sbml}'
                    )
            else: 
                sub_results_dic["Metabolites"]=id_unique_sbml
            logger.info(
                f'--"{db_list[-1]}" is present directly in '
                f"metabolic network with the corresponding ID "
                f'"{id_unique_sbml}" via the match ID "{met}"'
            )
        # Check for formula-based partial match
        if utils.check_formula_in_dict(sub_dict, met):
            sub_results_dic["Partial match"] = met
            logger.info(
                f'--""{met}"" has a partial match. We have a '
            f'formula as identifier for this metabolite: "{met}"'
        )
    
    return dic_tsv_results




def setup_match_db_sbml(
    meta_data_sbml,
    dic_tsv_results,
    dictionary_db,
    dic_couple_sbml,
    database_info,
    doublons,
    choice,
):
    """
    Performs matching between database metabolites and SBML metabolic networks.

    Args:
        meta_data_sbml (dict): Metadata of the SBML files, containing metabolite IDs.
        dic_tsv_results (list of dict): Current list of match results for metabolites.
        dic_couple_sbml (dict): Dictionary with SBML file names as
          keys and lists of metabolites as values.
        database_info (list of list): Each sublist contains all known
          IDs or names for a single metabolite.
        duplicates (list): List of metabolite IDs already matched (to
          avoid re-processing).
        choice (str): Either 'community' or 'none', determining the processing mode.

    Returns:
        dic_tsv_results (list of dict): Updated `dic_tsv_results` with
          any new matches found.
    """
    # Loop through each set of identifiers for one metabolite
    for db_list in database_info:

        temp_list = set()  # To store matched SBML networks temporarily
        set_list = db_list[-1]  # Usually the last item is the 'UNIQUE-ID'
        
        # Skip if this metabolite was already matched
        if set_list not in doublons:
            # Loop through all possible names/IDs for this metabolite
            for met_info in db_list:
                dic_tsv_results = match_db_sbml(
                    met_info,
                    meta_data_sbml,
                    dic_tsv_results,
                    dic_couple_sbml,
                    db_list,
                    set_list,
                    temp_list,
                    choice,
                )
    return dic_tsv_results


# ------------------------------------------------------------#
#             Partial Match Metabolites                      #
# ------------------------------------------------------------#


def partial_match_met_sbml(
    met,
    key_sub,
    meta_data_sbml,
    dictionary_db,
    dic_tsv_results,
    Match_id,
    dic_couple_sbml,
    doublons,
    choice,
    column_name,
    database_info,
    dic_temp,
    temp_list,
):
    """
    Handle partial matches between a metabolite and the SBML metabolic networks.

    Searches for partial matches of `met` within `meta_data_sbml`. If
    found, updates the `dic_tsv_results` with partial match
    information, depending on the mode specified by `choice`.

    In 'community' mode, collects all metabolic network names containing the match.
    In standard mode, records a direct match with the unique SBML ID.

    Also updates `Match_id`, `doublons`, and attempts to integrate
    this match into the database matching results.

    Args:
        met (str): Metabolite identifier to search for partial matches.
        key_sub (str): Original metabolite key from the input dataset.
        meta_data_sbml (dict): Dictionary containing SBML metabolite metadata.
        dic_tsv_results (list of dict): List of dictionaries storing match results.
        Match_id (dict): Dictionary mapping metabolite keys to matched IDs.
        dic_couple_sbml (dict): Maps SBML network names to lists of metabolites.
        doublons (list): List tracking metabolites already matched or
          identified as duplicates.
        choice (str): Mode of operation; 'community' or 'none'.
        column_name (str): Column name used to annotate how the match was made.
        database_info (list): List containing database matching metadata.
        dic_temp (dict): Temporary dictionary for current metabolite match info.
        temp_list (list): Temporary list of matched SBML network names
          (used in community mode).

    Returns:
        tuple: Updated (dic_tsv_results, Match_id, doublons,
        database_info, dic_temp, temp_list).
    """
    sub_dict = utils.find_sub_dict_by_nested_value(meta_data_sbml, met)


    if not sub_dict:
        return dic_tsv_results, Match_id, doublons, database_info, dic_temp, temp_list

    # Extract base unique SBML ID
    if sub_dict["ID"][0].endswith(']'):
        id_unique_sbml = sub_dict["ID"][0].rsplit("[", 1)[0]
    else:
        id_unique_sbml = sub_dict["ID"][0].rsplit("_", 1)[0]    

    if choice == "community":
        sbml_name = utils.find_key_by_list_value(dic_couple_sbml, id_unique_sbml)
        temp_list.append(sbml_name)
        dic_temp["Match in metabolic networks"] = list(set(temp_list))
    else:
        dic_temp["Match in metabolic networks"] = [id_unique_sbml]
        dic_temp[f"Match via {column_name}"] = "YES"

    dic_temp["Metabolites"] = key_sub
    Match_id[key_sub] = "NO UNIQUE-ID"

    # Append or extend the partial match string efficiently
    previous_partial = dic_temp.get("Partial match", "")
    dic_temp["Partial match"] = (
        met if not previous_partial else f"{previous_partial} _AND_ {met}"
    )

    logger.info(
        f'      --"{key_sub}" has a partial match. A match was found '
        f'with the ID: "{met}" via: {column_name}'
    )

    # Append dic_temp only if new to results
    if dic_temp not in dic_tsv_results:
        dic_tsv_results.append(dic_temp)
        doublons.append(key_sub)

    # Update matches further in the database (partial mode)
    dic_tsv_results, Match_id, database_info = identification_sbml_match_into_db(
        dictionary_db,
        met,
        column_name,
        dic_tsv_results,
        Match_id,
        database_info,
        key_sub,
        "partial",
    )
    return dic_tsv_results, Match_id, doublons, database_info, dic_temp, temp_list





# ---------------------------------------#
#               MAPPING                 #
# ---------------------------------------#


def mapping_run(
    output_folder,
    dictionary_db,
    maf_dictionnary,
    keys,
    maf_df,
    meta_data_sbml,
    dic_couple_sbml,
    start_time,
    partial_match,
    quiet,
    timestamp,
    choice,
):
    """
    Centralises the mapping step, including data preparation,
    matching/unmatching processes, and result compilation. At the end,
    generates a TSV file with the mapping results.

    Args:
        output_folder (str or Path): Path to the output directory.
        dictionary_db (dict): Dictionary where each key corresponds to
          a metabolite from the MetaCyc/MetaNetX database and the values contain
          information such as IDs from other databases.
        maf_dictionnary (dict): Dictionary containing data from the
          MAF file used for matching against the conversion datatable.
        maf_df (pandas.DataFrame): DataFrame version of the MAF file,
          used for extracting CHEBI/InChIKeys.
        columns_name_maf (list): List of relevant column names from
          the MAF dictionary (after filtering out empty or irrelevant
          columns).
        keys (list): List of all possible column names expected in the
          output or input files, used to standardize/harmonize the final
          output.
        List_merge_sbml_metabolites (list): List of all metabolites
          present in the SBML files.
        meta_data_sbml (dict): Metadata extracted from the SBML files
          (e.g., IDs, names, formulas).
        dic_couple_sbml (dict): Dictionary where each key is an SBML
          file name and each value is the list of metabolites it
          contains.
        start_time (int or str): Timestamp marking the start of
          execution, used for naming output files uniquely.
        timestamp (int): Begin time of the run
        partial_match (str):  Defines if the script is run
          in partial_match option or not.
        choice (str): Either 'community' or 'none'. Defines if the
          script is run in community mode or classic mode.

    Returns:
        None. Writes output to a TSV file in the specified output folder.
    """

    # ---------------------------#
    #  Set output format part   #
    # ---------------------------#

    # Results file
    Match_id = {}
    doublons = []
    database_info = []
    dic_tsv_results = []

    List_maf_metabolites = list(itertools.chain.from_iterable(maf_dictionnary.values()))
    List_maf_metabolites_wt_nan = list(
        dict.fromkeys([x for x in List_maf_metabolites if x != "nan"])
    )

    # ---------------#
    #  Match part   #
    # ---------------#

    logger.info("\n\n----------------------------------------------")
    logger.info("---------------MATCH STEP 1-------------------")
    logger.info("----------------------------------------------\n")

    logger.info(
        "<1> Direct matching test between metabolites derived from "
        "metabolomic data on all metadata in the metabolic network"
    )
    logger.info(
        "<2> Matching test between metabolites derived from "
        "metabolomic data on all metadata in the database conversion"
    )

    for column_name, value in maf_dictionnary.items():
        list_maf_metabolites_wt_nan = [x for x in value if x != "nan"]
        for met in list_maf_metabolites_wt_nan:
            logger.info(f'\n++ Match step for "{met}":')
            dic_tsv_results, Match_id, doublons, database_info = match_met_sbml(
                met,
                meta_data_sbml,
                dictionary_db,
                dic_tsv_results,
                Match_id,
                dic_couple_sbml,
                doublons,
                choice,
                column_name,
                database_info,
            )
            dic_tsv_results, Match_id, database_info = match_metabo(
                dictionary_db,
                met,
                column_name,
                dic_tsv_results,
                Match_id,
                database_info,
                key_sub=None,
                dic_temp_db=None,
                partial=False,
            )

    logger.info("\n\n----------------------------------------------")
    logger.info("---------------MATCH STEP 2-------------------")
    logger.info("----------------------------------------------\n")

    logger.info(
        "<3> Matching test on metabolites that matched only on the "
        "database conversion data against all metadata from the "
        "metabolic network\n"
    )

    dic_tsv_results = setup_match_db_sbml(
        meta_data_sbml,
        dic_tsv_results,
        dictionary_db,
        dic_couple_sbml,
        database_info,
        doublons,
        choice,
    )

    # Groups similar dictionaries based on shared values in key fields, then merges
    # them.
    dic_tsv_results = utils.smart_merge(dic_tsv_results)

    if partial_match:
        logger.info("\n\n------------------------------------------------")
        logger.info("---------------PARTIAL MATCH -------------------")
        logger.info("----------------------------------------------\n")
        logger.info(
            "<4> Attempting to find new IDs for unmatched metabolites "
            "using multiple strategies: removing enantiomer "
            "specificity, using the core part of InChIKeys, or "
            "exploring parent/child relationships in CHEBI.\n"
        )

        dic_unmatch_to_reload = {}

        # Filter metabolites absent in both database and metabolic network
        unmatch_metabolites_try = list(
            set(List_maf_metabolites_wt_nan) - set(Match_id.keys())
        )
        unmatch_metabolites = utils.process_unmatches(
            maf_df, set(Match_id.keys()), unmatch_metabolites_try
        )

        list_unmatch_to_reload = {}
        if any(col.lower() == "chebi" for col in maf_df.columns):
            logger.info("\n-----> CHEBI <-----")
            # Extract the chebi from the maf datatable merge
            dic_chebi_match = utils.find_targets_with_chebi(maf_df, unmatch_metabolites)

            list_unmatch_to_reload = asyncio.run(utils.chebi_ontology_main_process(dic_chebi_match))
            dic_unmatch_to_reload["CHEBI"] = list_unmatch_to_reload


        logger.info("\n-----> inchikey <-----")
        dic_Inchey_match = {
            i: [i.split("-")[0]]
            for i in unmatch_metabolites
            if "inchikey" in str(i).lower()
        }
        for key, value in dic_Inchey_match.items():
            logger.info(f"inchikey: {key} -> Short inchikey: {value}")
        dic_unmatch_to_reload["inchikey"] = dic_Inchey_match

        # ------------------------------------------------------------------------- #
        # Remove the L - D - R -S  enantiomerS if the opt is true and
        # update the datatable conversion temporary for the mapping.
        # ------------------------------------------------------------------------- #
        logger.info("\n-----> Enantiomers <-----")
        dic_enantiomers_match = list(
            set(unmatch_metabolites)
            - set(list_unmatch_to_reload.keys())
            - set(dic_Inchey_match.keys())
        )
        dic_unmatch_to_reload["Enantiomers"] = dic_enantiomers_match
        logger.info(
            "-----> Remove enantiomers in database and in metadata of sbml <-----"
        )

        dictionary_db_enantiomers = remove_enantiomer_and_Inchey_db(dictionary_db)
        dictionary_metadata_enantiomers = remove_enantiomer_and_Inchey_metadata(
            meta_data_sbml
        )

        logger.info("\n\n----------------------------------------------------")
        logger.info("---------------Retry MATCH STEP 1-------------------")
        logger.info("----------------------------------------------------")
        database_info = []

        for column_name, value in dic_unmatch_to_reload.items():
            if column_name == "CHEBI":
                logger.info("\n-----> Test: CHEBI <-----")
                for key_sub, val_sub in value.items():
                    dic_temp_sbml = {}
                    dic_temp_db = {}
                    temp_list = []
                    dic_temp_sbml["Partial match"] = ""
                    dic_temp_sbml["Match in database"] = ""
                    logger.info(f'\n++ Match step for "{key_sub}":')
                    for met in val_sub:
                        logger.info(f'\n--Try with {met}":')
                        (
                            dic_tsv_results,
                            Match_id,
                            doublons,
                            database_info,
                            dic_temp_sbml,
                            temp_list,
                        ) = partial_match_met_sbml(
                            met,
                            key_sub,
                            meta_data_sbml,
                            dictionary_db,
                            dic_tsv_results,
                            Match_id,
                            dic_couple_sbml,
                            doublons,
                            choice,
                            column_name,
                            database_info,
                            dic_temp_sbml,
                            temp_list,
                        )
                        dic_tsv_results, Match_id, database_info, dic_temp_db = (
                            match_metabo(
                                dictionary_db,
                                met,
                                column_name,
                                dic_tsv_results,
                                Match_id,
                                database_info,
                                key_sub,
                                dic_temp_db,
                                "partial",
                            )
                        )
            elif column_name == "inchikey":
                logger.info("\n-----> Test: Inchey <-----")
                for key_sub, val_sub in value.items():
                    dic_temp_sbml = {}
                    dic_temp_db = {}
                    temp_list = []
                    met = val_sub[0]
                    logger.info(f'\n++ Match step for "{met}":')
                    logger.info(f'\n--Try with {key_sub}":')
                    (
                        dic_tsv_results,
                        Match_id,
                        doublons,
                        database_info,
                        dic_temp_sbml,
                        temp_list,
                    ) = partial_match_met_sbml(
                        met,
                        key_sub,
                        dictionary_metadata_enantiomers,
                        dictionary_db,
                        dic_tsv_results,
                        Match_id,
                        dic_couple_sbml,
                        doublons,
                        choice,
                        column_name,
                        database_info,
                        dic_temp_sbml,
                        temp_list,
                    )
                    dic_tsv_results, Match_id, database_info, dic_temp_db = (
                        match_metabo(
                            dictionary_db_enantiomers,
                            met,
                            column_name,
                            dic_tsv_results,
                            Match_id,
                            database_info,
                            key_sub,
                            dic_temp_db,
                            "partial",
                        )
                    )
            else:
                logger.info("\n-----> Test: Enantiomers <-----")
                for met in value:
                    dic_temp_sbml = {}
                    dic_temp_db = {}
                    temp_list = []
                    logger.info(f'\n++ Match step for "{met}":')
                    (
                        dic_tsv_results,
                        Match_id,
                        doublons,
                        database_info,
                        dic_temp_sbml,
                        temp_list,
                    ) = partial_match_met_sbml(
                        met,
                        met,
                        dictionary_metadata_enantiomers,
                        dictionary_db,
                        dic_tsv_results,
                        Match_id,
                        dic_couple_sbml,
                        doublons,
                        choice,
                        column_name,
                        database_info,
                        dic_temp_sbml,
                        temp_list,
                    )
                    dic_tsv_results, Match_id, database_info, dic_temp_db = (
                        match_metabo(
                            dictionary_db_enantiomers,
                            met,
                            column_name,
                            dic_tsv_results,
                            Match_id,
                            database_info,
                            met,
                            dic_temp_db,
                            "partial",
                        )
                    )

        logger.info("\n\n----------------------------------------------------")
        logger.info("---------------Retry MATCH STEP 2-------------------")
        logger.info("----------------------------------------------------")

        dic_tsv_results = setup_match_db_sbml(
            meta_data_sbml,
            dic_tsv_results,
            dictionary_db,
            dic_couple_sbml,
            database_info,
            doublons,
            choice,
        )
        dic_tsv_results = setup_match_db_sbml(
            dictionary_metadata_enantiomers,
            dic_tsv_results,
            dictionary_db,
            dic_couple_sbml,
            database_info,
            doublons,
            choice,
        )

        # Groups similar dictionaries based on shared values in key
        # fields, then merges them.
        dic_tsv_results = utils.smart_merge(dic_tsv_results)

    #    #----------------------------#
    #    #  Umatch set up the output  #
    #    #----------------------------#
    unmatch_metabolites_try_last = list(
        set(List_maf_metabolites_wt_nan) - set(Match_id.keys())
    )
    unmatch_metabolites_total = utils.process_unmatches(
        maf_df, set(Match_id.keys()), unmatch_metabolites_try_last
    )
    unmatch_metabolites_merged = utils.extract_metabolite_combinations(
        unmatch_metabolites_total, maf_df
    )

    keys_starter = [
        "Metabolites",
        "Match in database",
        "Match in metabolic networks",
        "Partial match",
    ]
    dic_tsv_results, keys_reorder = setup_harmonisation_output(
        dic_tsv_results, keys_starter, unmatch_metabolites_merged, keys
    )

    #      #-----------------------------#
    # #    #   Results User Interface    #
    # #    #-----------------------------#

    stats = utils.analyze_column_matches(
        dict_list=dic_tsv_results,
        col_db="Match in database",
        col_net="Match in metabolic networks",
        col_partial="Partial match",
    )
    # Terminal results
    logger.info("\n-------------------- SUMMARY REPORT --------------------\n")

    logger.info("\nRecap of Matches:")
    logger.info("  + Matched metabolites: %s", stats["network_total_filled"])
    logger.info("  + Unmatched metabolites: %s", stats["network_empty_total"])
    logger.info(
        "  + Partial matches: %s",
        stats["partial_and_metabolic_filled"] + stats["db_and_partial_only"],
    )

    logger.info("\n Match Details:")
    logger.info(f"  --> Full match (database + SBML): {stats['both_filled']}")
    logger.info(
        f"  --> Partial match + metabolic info: {stats['partial_and_metabolic_filled']}"
    )
    logger.info(f"  --> Match only in SBML: {stats['network_only']}")

    logger.info("\n Unmatch Details:")
    logger.info(f"  --> Full unmatch (no match in DB or SBML): {stats['both_empty']}")
    logger.info(f"  --> Match in DB but not in SBML: {stats['db_only']}")
    logger.info(f"  --> Partial match in DB only: {stats['db_and_partial_only']}")

    logger.info("\n--------------------------------------------------------\n")

    # Write output file in funtion of the "choice"
    if partial_match:
        if choice == "community":
            utils.write_tsv(
                dic_tsv_results,
                output_folder,
                f"{choice}_mapping_results_partial_match_{start_time}.tsv",
                keys_reorder,
                quiet,
            )  # Write results
        else:
            utils.write_tsv(
                dic_tsv_results,
                output_folder,
                f"mapping_results_partial_match_{start_time}.tsv",
                keys_reorder,
                quiet,
            )  # Write results
    else:
        if choice == "community":
            utils.write_tsv(
                dic_tsv_results,
                output_folder,
                f"{choice}_mapping_results_{start_time}.tsv",
                keys_reorder,
                quiet,
            )  # Write results
        else:
            utils.write_tsv(
                dic_tsv_results,
                output_folder,
                f"mapping_results_{start_time}.tsv",
                keys_reorder,
                quiet,
            )  # Write results
    if quiet:
        print(
            "\n--- Total runtime %.2f seconds ---\n ---> MAPPING COMPLETED'"
            % (time.time() - timestamp)
        )
