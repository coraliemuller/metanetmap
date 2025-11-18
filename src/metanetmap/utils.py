#!/bin/python
# MISTIC Project INRIA/INRAE
# Author Muller Coralie
# Date: 2025/06/30
# Update: 2025/08/-

import aiohttp
import ast
import asyncio
import csv
import importlib.resources
import logging
import os
import re
import sys
from tqdm.asyncio import tqdm_asyncio
from collections import defaultdict
from importlib import metadata  # allows you to query the installed versions
from pathlib import Path

import pandas as pd

logger = logging.getLogger("Mapping")


# ----------------------------------------------------#
#             UTILS -> File management               #
# ----------------------------------------------------#


def get_files_from_package_dir(package_dir: str):
    """
    Given a package directory (dot-separated), return a list of
    pathlib.Path objects representing all files inside that directory.

    This uses importlib.resources to access package data and ensures
    the returned paths are real filesystem paths (works even if package
    is zipped).

    Args:
        package_dir (str): Package directory path in dot notation
                           e.g. "metanetmap.test_data.data_test.toys.maf"

    Returns:
        List[Path]: List of pathlib.Path objects to files inside the
        package directory. The paths are valid only inside the context
        of the `with` block.
    """
    file_paths = []
    # Get a Traversable resource for the package directory
    resource_dir = importlib.resources.files(package_dir)

    # Use as_file context manager to get a real filesystem path
    with importlib.resources.as_file(resource_dir) as real_dir:
        # Iterate over items in the directory
        for item in real_dir.iterdir():
            # Only include files, skip subdirectories
            if item.is_file():
                file_paths.append(item)

    return file_paths


def is_valid_file(filepath):
    """Return True if filepath exists

    Args:
        filepath (str): path to file

    Returns:
        bool: True if path exists, False otherwise
    """
    try:
        open(filepath, "r").close()
        return True
    except OSError:
        logger.warning('The file "%s" is not existing file.', filepath)
        sys.exit()
        return False


def is_valid_dir(dirpath):
    """Return True if directory exists or can be created (then create
    it).

    Args:
        dirpath (str): path of directory

    Returns:
        bool: True if dir exists, False otherwise
    """
    if not os.path.isdir(dirpath):
        try:
            os.makedirs(dirpath)
            return True
        except OSError:
            return False
    else:
        return True


def is_valid_path(filepath):
    """True if given filepath is a valid one."""
    if filepath and not os.access(filepath, os.W_OK):
        logger.warning('The path "%s" is not existing but can be created.', filepath)
        sys.exit()
    else:
        return True


def is_valid_file_or_create(filepath):
    """
    True if given filepath is a valid one (a file exists, or could
    exist).
    """
    if filepath and not os.access(filepath, os.W_OK):
        try:
            open(filepath, "w").close()
            os.unlink(filepath)
            return True
        except OSError:
            return False
    else:
        return True


def write_tsv(dic, output_folder, output_name, keys_reorder, quiet):
    """
    Write a tsv file from a dictionary

    Args:
        dic (dic): Dictionnary with information [{KEY1: VALUE1, KEY2:
          VALUES2, KEY3: VALUES3},{KEY1: VALUE1, KEY2: VALUES2, KEY3:
          VALUES3}]
        output_folder (path):  Path to create the output file
        output_name (str): Output name
        keys_reorder (list): Possible to give a list of colnames to
          reorder the columns in the dataframe
    """
    df = pd.DataFrame.from_dict(dic)
    if keys_reorder:
        df = df[keys_reorder]
    path_output = os.path.join(output_folder, output_name)
    if not quiet:
        logger.info(f"Output file successfully written to: {path_output}")
    else:
        print(f"\nOutput file successfully written to: {path_output}")
    df.to_csv(path_output, sep="\t", index=None)


def remove_empty_keys(dic_to_clean):
    """
    Remove all key-value where value is empty to avoid empty columns
    later.

    Args:
        dic_to_clean (dic): dictionnary with empty value

    Returns:
        dic (dic): dictionnary without empty value
    """
    dic = {key: val for key, val in dic_to_clean.items() if val}
    return dic


def write_csv(dictionary_db, output_file, original_keys):
    """
    Writes the dictionary of metabolites to a TSV file, preserving the
    order of original columns and appending any new columns at the end
    (in the order they appear in the data).

    Args:
        dictionary_db (list of dict): List of metabolite dictionaries.
        output_file (str): Path to output TSV file.
        original_keys (list): Ordered list of known column names to
          appear first.
    """
    # Remove possible MetaCyc header line
    dictionary_db_clean = [
        row
        for row in dictionary_db
        if row.get("UNIQUE-ID") and not row["UNIQUE-ID"].startswith("#")
    ]

    # Track all keys seen in the data
    seen_keys = set(original_keys)
    new_keys = []

    for row in dictionary_db_clean:
        for key in row:
            if key not in seen_keys:
                new_keys.append(key)
                seen_keys.add(key)

    # Final fieldnames: known keys + new keys in order of appearance
    final_keys = original_keys + new_keys

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=final_keys, delimiter="\t")
        writer.writeheader()
        writer.writerows(dictionary_db_clean)


# --------------------------------------------------------------#
#             UTILS -> LOGS and TESTS management               #
# --------------------------------------------------------------#


class LeveledFormatter(logging.Formatter):
    """
    A custom logging formatter that allows different format styles per
    log level.

    Example:
        formatter = LeveledFormatter("%(message)s")
        formatter.set_formatter(logging.ERROR,
          logging.Formatter("[ERROR] %(message)s"))
        formatter.set_formatter(logging.DEBUG,
          logging.Formatter("[DEBUG] %(asctime)s - %(message)s"))
    """

    def __init__(self, default_fmt):
        """
        Initializes the formatter with a default format string.

        Args:
            default_fmt (str): The default format string to be used if
              no level-specific formatter is set.
        """
        super().__init__(default_fmt)
        self._formatters = {}  # Dictionary to store formatters per log level

    def set_formatter(self, level, formatter):
        """
        Associates a specific formatter with a logging level.

        Args:
            level (int): The log level (e.g., logging.ERROR,
              logging.INFO).
            formatter (logging.Formatter): A formatter instance to use
              for that level.
        """
        self._formatters[level] = formatter

    def format(self, record):
        """
        Formats the log record using the formatter associated with its
        log level, or the default formatter if none is set.

        Args:
            record (LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message.
        """
        # Use the formatter for the specific log level if available
        formatter = self._formatters.get(record.levelno, self)
        return formatter.format(record)


def get_logger(name=None, level=logging.DEBUG):
    """
    Get a logger instance by name.
    If the logger has no handlers, configure a simple console handler.
    This prevents duplicate handlers on multiple imports.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


def setup_full_logger(args, start_time):
    """
    Setup the root logger with file and console handlers,
    based on command line args such as --quiet or --build_db.
    Use custom formatter (e.g., utils.LeveledFormatter) if needed.
    """
    # Suppressing warnings when loading model from file in cobra
    logging.getLogger("cobra").setLevel(logging.ERROR)

    root_logger = logging.getLogger("Mapping")
    # Remove all existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(logging.DEBUG)

    # Create your custom formatter here, or use a simple one
    formatter = LeveledFormatter("%(message)s")
    formatter.set_formatter(logging.INFO, logging.Formatter("%(message)s"))
    formatter.set_formatter(
        logging.WARNING,
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )
    formatter.set_formatter(
        logging.CRITICAL,
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )

    # File handler for logs (unless building db)
    if args.cmd != "build_db":
        if args.cmd == "test":
            USER_DIR = Path.cwd()
            toys_paths = USER_DIR / "toys/logs/"
            is_valid_dir(USER_DIR / "toys/logs/")
            log_dir = toys_paths
        else:
            if args.output_folder:
                is_valid_dir(f"{args.output_folder}/logs/")
                log_dir = f"{args.output_folder}/logs/"
            else:
                USER_DIR = Path.cwd()
                is_valid_dir(USER_DIR / "mapping/logs/")
                log_dir = USER_DIR / "mapping/logs/"

        log_file = os.path.join(log_dir, f"mapping_{start_time}.log")
        file_handler = logging.FileHandler(log_file, mode="w+")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Console handler with quiet mode option
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    if args.quiet and args.cmd != "build_db":
        console_handler.setLevel(logging.WARNING)
        print("---->    Mapping run in quiet mode    <----")
    root_logger.addHandler(console_handler)

    return root_logger


def log_package_versions(packages):
    """
    Logs the installed version of each package in the provided list.

    Args:
        packages (list of str): A list of package names (as strings) to
        check.

    Logs:
        - INFO message with the package name and version if it is
          installed.
        - WARNING message if the package is not installed.
    """
    for package in packages:
        try:
            version = metadata.version(package)
            logger.info(f"{package} version: {version}")
        except metadata.PackageNotFoundError:
            logger.warning(f"{package} is not installed.")


# ----------------------------------------------------#
#             UTILS -> Chebi management              #
# ----------------------------------------------------#
MAX_CONCURRENT_REQUESTS = 20
sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def fetch_chebi_entity(session, chebi_id):
    """
    Asynchronously fetch a ChEBI entity from the ChEBI 2.0 REST API.

    This function retrieves detailed compound data for a given ChEBI ID.
    It automatically accepts both plain numeric IDs (e.g. "15377") and
    full IDs (e.g. "CHEBI:15377").

    Parameters
    ----------
    session : aiohttp.ClientSession
        An active aiohttp client session used for making HTTP requests.

    chebi_id : str
        The ChEBI compound identifier. Can be provided as either:
        - "CHEBI:XXXX" (full form)
        - "XXXX" (numeric form only)

    Returns
    -------
    dict or None
        A Python dictionary representing the ChEBI compound data if
        the request succeeds (HTTP 200). Returns `None` if the request
        fails or an exception occurs.

    Notes
    -----
    - The API endpoint used is:
      https://www.ebi.ac.uk/chebi/backend/api/public/compound/{CHEBI_ID}/
    - The query parameters restrict the response to ontology information only.
    - A concurrency semaphore (`sem`) is used to limit parallel requests.
    """
    # Normalize the ChEBI ID format (ensure it starts with "CHEBI:")
    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    # Construct the REST API endpoint for the given compound
    url = (
        f"https://www.ebi.ac.uk/chebi/backend/api/public/compound/"
        f"{chebi_id}/?only_ontology_parents=false&only_ontology_children=false"
    )

    try:
        # Use a semaphore to avoid sending too many requests at once
        async with sem:
            # Perform the GET request within the provided aiohttp session
            async with session.get(url) as response:
                # Check if the request succeeded
                if response.status != 200:
                    logger.error(f"Failed to fetch {chebi_id} (HTTP {response.status})")
                    return None

                # Parse and return the JSON body
                return await response.json()

    except Exception as e:
        # Catch network or parsing errors and log them
        logger.error(f"Error fetching {chebi_id}: {e}")
        return None



def get_chebi_links(entity_json) :
    """
    Extracts parent/child ("outgoing"/"incoming") relationships
    from a ChEBI 2.0 JSON API response.

    The ChEBI API provides ontology relationships for each entity.
    - "outgoing_relations" correspond to parent relationships (e.g. compound → class)
    - "incoming_relations" correspond to child relationships (e.g. subclass → compound)
    """
    relation_chebi_dic = {"outgoings": [], "incomings": []}
    ontology = entity_json.get("ontology_relations", {})

    outgoing_relations = ontology.get("outgoing_relations", []) or []
    incoming_relations = ontology.get("incoming_relations", []) or []

     # --- Outgoing relations (PARENTS) ---
    for rel in outgoing_relations:
        # Keep only "is a" relationships, as they represent ontology hierarchy
        if rel and rel.get("relation_type") == "is a":
            chebi_id = rel.get("final_id")
            clean_text_outgoing = re.sub(r'<.*?>', '', rel.get("final_name"))
            relation_chebi_dic["outgoings"].append({
                "chebi_id": str(chebi_id),
                "name": clean_text_outgoing
            })

    # --- Incoming relations (CHILDREN) ---
    for rel in incoming_relations:
        # Keep only "is a" relationships, as they represent ontology hierarchy
        if rel and rel.get("relation_type") == "is a":
            chebi_id = rel.get("init_id")
            clean_text_incoming = re.sub(r'<.*?>', '', rel.get("init_name"))
            relation_chebi_dic["incomings"].append({
                "chebi_id": str(chebi_id),
                "name": clean_text_incoming
                })
    return relation_chebi_dic




def chebi_parents_childrens(list_unmatch_to_reload, list_relation_chebi, key):
    """
    Update the output data structure with parent/child relationships.

    This function takes a dictionary of ontology relations (from ChEBI),
    and adds all related parent and child entities to a results dictionary.

    Parameters
    ----------
    list_unmatch_to_reload : dict
        The main data structure being built during processing.
        Keys represent the input compounds, and values are lists
        containing related ChEBI IDs and names.

    list_relation_chebi : dict
        A dictionary containing two lists:
          - "outgoings": list of parent relationships
          - "incomings": list of child relationships
        Each element of the list is expected to have keys:
        - "chebi_id": the related ChEBI numeric ID (string)
        - "name": the related compound name (optional)

    key : str
        The current compound key being processed (e.g. "water").

    Returns
    -------
    dict
        The same `list_unmatch_to_reload` dictionary, updated in place
        with new parent and child relationships for the given key.
    """

    # Iterate over both parent ("outgoings") and child ("incomings") lists
    for key_type, entry_list in list_relation_chebi.items():
        # Log what type of relations we're about to process
        if key_type == "outgoings" and entry_list:
            logger.info("   --Parents are :")
        elif key_type == "incomings" and entry_list:
            logger.info("   --Children are : ")

        # Loop over each related entity in the current list
        for entry in entry_list:
            # Construct a formatted ChEBI ID string (CHEBI:xxxx)
            short_chebi = f"CHEBI:{entry['chebi_id']}"
            name = entry.get("name")

            # If the related entity has a name, add both ID and name
            if name:
                list_unmatch_to_reload[key].extend([short_chebi, name])
                logger.info(f"     -- {key} is related to {name}")
            else:
                # If no name is available, store only the ID
                list_unmatch_to_reload[key].append(short_chebi)
                logger.info(f"     -- {key} has no name.")

    return list_unmatch_to_reload




async def process_chebi(session, key, value, list_unmatch_to_reload):
    """
    Process a single ChEBI identifier (compound).

    This coroutine:
    1. Fetches the ChEBI entity data from the ChEBI REST API.
    2. Logs the entity’s name and identifier.
    3. Extracts its ontology relations (parents and children).
    4. Updates the main results dictionary with this information.

    Parameters
    ----------
    session : aiohttp.ClientSession
        An active aiohttp session used for making HTTP requests.

    key : str
        The key name (usually a local or user-friendly name for the compound).

    value : str
        The ChEBI ID to process (can be "CHEBI:xxxx" or "xxxx").

    list_unmatch_to_reload : dict
        A shared dictionary that will be updated with the ChEBI entity data
        and its parent/child relationships.

    Returns
    -------
    None
        The function modifies `list_unmatch_to_reload` in place.
    """
    # Log which compound is being processed
    logger.info(f"\n ++CHEBI identification step for {value}:")

    # Fetch the entity JSON from the ChEBI API (asynchronously)
    entity = await fetch_chebi_entity(session, value)
    if not entity:
        # If no data was retrieved, stop processing this entry
        return

    # Retrieve the ChEBI accession (main identifier) from the response
    entity_name = entity.get("chebi_accession")
    logger.info(f"--{value} is {entity_name}")

    # Initialize this key with the main entity name
    list_unmatch_to_reload[key] = [entity_name]
    list_unmatch_to_reload[key].append(entity.get("name"))


    # Vérifie l'existence et récupère la valeur
    manual_xrefs = entity.get("database_accessions", {}).get("MANUAL_X_REF", [])

    for xref in manual_xrefs:
        if xref.get("source_name") == "MetaCyc":
            accession = xref.get("accession_number")
            list_unmatch_to_reload[key].append(accession)

    # Extract parent and child ontology relations from the ChEBI JSON
    relation_chebi = get_chebi_links(entity)
    # Update the results dictionary with parent/child info
    chebi_parents_childrens(list_unmatch_to_reload, relation_chebi, key)


async def chebi_ontology_main_process(dic_chebi_match):
    """
    Main asynchronous routine to process multiple ChEBI identifiers in parallel.

    This function:
      1. Creates a shared aiohttp session for all requests.
      2. Launches asynchronous tasks for each ChEBI compound to process
         (via `process_chebi`).
      3. Uses tqdm for a progress bar if logging is set to INFO level.
      4. Returns a dictionary summarizing all processed ChEBI entities
         and their ontology relationships.

    Parameters
    ----------
    dic_chebi_match : dict
        A dictionary mapping user-friendly names (keys) to ChEBI identifiers (values).
        Example:
            {
                "water": "CHEBI:15377",
                "hydron": "CHEBI:15379"
            }

    Returns
    -------
    dict
        A dictionary of the form:
            {
                "CHEBI": {
                    "water": [...],
                    "hydron": [...]
                }
            }

    Notes
    -----
    - Uses asyncio.gather() to process all entries concurrently.
    - Progress bar (`tqdm_asyncio.gather`) is displayed only if logger level is INFO.
    - Each task internally calls `process_chebi()`.
    """

    # Dictionary that will hold all processed ChEBI results
    list_unmatch_to_reload = {}

    # Create a single shared HTTP session for all API calls
    async with aiohttp.ClientSession() as session:
        # Create one async task per ChEBI compound to process
        tasks = [
            process_chebi(session, key, value, list_unmatch_to_reload)
            for key, value in dic_chebi_match.items()
        ]

        # Run tasks concurrently
        # If logger is in INFO mode → show progress bar using tqdm
        if logger.isEnabledFor(logging.INFO):
            await tqdm_asyncio.gather(*tasks, desc="Fetching ChEBI data")
        else:
            await asyncio.gather(*tasks)

    # Return the final structured result containing all ChEBI data
    return list_unmatch_to_reload



def find_targets_with_chebi(df, targets):
    """
    For each target, search in all columns (including 'CHEBI') of the
    DataFrame. Ignore cells that are NaN. If a match is found and the
    'CHEBI' value in that row is not null, not 'nan' string, and not
    empty, return a dictionary mapping {target: CHEBI}.
    """
    result = {}

    for target in targets:
        for _, row in df.iterrows():
            chebi = row.get("CHEBI", None)

            # Skip rows with missing, empty, or 'nan' CHEBI (string)
            if (
                pd.isna(chebi)
                or str(chebi).strip().lower() == "nan"
                or str(chebi).strip() == ""
            ):
                continue

            # Check each cell in the row
            for value in row:
                if pd.isna(value):
                    continue  # Skip NaN values

                if isinstance(value, list):
                    if target in value:
                        result[target] = str(chebi)
                        break
                else:
                    if str(value).strip() == str(target).strip():
                        result[target] = str(chebi)
                        break

            if target in result:
                break  # Found a match, go to next target

    return result


# ----------------------------------------------------#
#             UTILS -> UI management                 #
# ----------------------------------------------------#

# Function to check whether a value is ‘filled in’


def cell_is_full(value):
    """
    Helper function to check if a cell is considered 'filled'.
    A cell is full if it's not None, not an empty string, and not just
    whitespace.
    """
    return bool(value and str(value).strip())


def analyze_column_matches(dict_list, col_db, col_net, col_partial=None):
    """
    Generalized function to analyze matches between database and network
    columns, and optionally a third 'Partial match' column.

    It returns counts for:
        - Both DB and network columns filled.
        - Both DB and network columns empty.
        - Network filled and DB empty.
        - DB filled and network empty.
        - Total cases where network is filled.
        - Total cases where network is empty.
        - Cases where 'Partial match' and network are filled (if
          col_partial is provided).
        - Cases where only DB and partial match are filled (and network
    is empty).

    Parameters:
        dict_list (list[dict]): List of dictionaries (rows).
        col_db (str): Key name for the database match column.
        col_net (str): Key name for the metabolic/network match column.
        col_partial (str, optional): Key name for the partial match
          column.

    Returns:
        dict: A dictionary with detailed match statistics.
    """

    stats = {
        "both_filled": 0,
        "both_empty": 0,
        "network_only": 0,
        "db_only": 0,
        "network_total_filled": 0,
        "network_empty_total": 0,
    }

    if col_partial:
        stats["partial_and_metabolic_filled"] = 0  # <-- new name for updated logic
        stats["db_and_partial_only"] = 0

    for row in dict_list:
        db_filled = cell_is_full(row.get(col_db))
        net_filled = cell_is_full(row.get(col_net))
        partial_filled = cell_is_full(row.get(col_partial)) if col_partial else False

        if db_filled and net_filled:
            stats["both_filled"] += 1
        elif not db_filled and not net_filled:
            stats["both_empty"] += 1
        elif net_filled and not db_filled:
            stats["network_only"] += 1
        elif db_filled and not net_filled:
            stats["db_only"] += 1

        if net_filled:
            stats["network_total_filled"] += 1
        else:
            stats["network_empty_total"] += 1

        if col_partial:
            # New logic: partial + metabolic filled (DB doesn't matter)
            if net_filled and partial_filled:
                stats["partial_and_metabolic_filled"] += 1

            # Only DB and Partial filled, but not network
            if db_filled and not net_filled and partial_filled:
                stats["db_and_partial_only"] += 1

    return stats


# ----------------------------------------------------#
#             UTILS -> Search management             #
# ----------------------------------------------------#


def fix_arrows_in_parentheses(text):
    """
    Replaces all '?' characters inside parentheses with '->'.

    This function scans the input text for any substrings inside a
    single pair of parentheses (i.e., non-nested), and replaces every
    occurrence of '?' within those parentheses with '->'.

    Args:
        text (str): The input string that may contain parentheses with
        '?' inside.

    Returns:
        str: The modified string with '?' replaced by '->' only inside
        parentheses.

    Example:
        Input: "A (? B) and C (? D)"
        Output: "A (-> B) and C (-> D)"
    """
    return re.sub(r"\(([^()]+)\)", lambda m: f"({m.group(1).replace('?', '->')})", text)



def find_all_sub_dicts_by_nested_value(data: dict, search_value: str):
    """
    Searches inside a nested dictionary (dictionary of dictionaries)
    for all sub-dictionaries that contain a list with a string equal to
    `search_value` (case-insensitive match).

    Args:
        data (dict): The main dictionary to search through.
        search_value (str): The string value to search for
        (case-insensitive).

    Returns:
        list: A list of all matching sub-dictionaries. Empty list if none found.
    """
    return [
        v
        for v in data.values()  # Iterate over all sub-dictionaries
        if isinstance(v, dict)
        and any(
            isinstance(val, list)
            and any(
                isinstance(el, str) and el.lower() == search_value.lower()
                for el in val  # Compare each string element in the list
            )
            for val in v.values()  # Iterate over all values in the sub-dictionary
        )
    ]



def find_dict_by_metabolite(dic_tsv_results: list, met: str):
    """
    Search through a list of dictionaries to find the first dictionary
    where the value associated with the key 'Metabolites' equals the
    target `met`.

    Args:
        dic_tsv_results (list): List of dictionaries to search.
        met (str): The metabolite value to look for.

    Returns:
        dict or None: The first dictionary where 'Metabolites' == met,
        or None if not found.
    """
    for dic in dic_tsv_results:
        # Check if 'Metabolites' key exists and equals met
        if "Metabolites" in dic and dic["Metabolites"] == met:
            return dic
    return None


def find_keys_with_value_in_dict(data_dict, search_value):
    """
    Finds all keys in a dictionary whose associated values contain the
    given search value, using lowercase comparison (case-insensitive
    match).

    Assumes that the values in the dictionary are iterable (e.g., lists,
    sets, tuples), and all elements (including search_value) will be
    converted to lowercase for comparison.

    Args:
        data_dict (dict): Dictionary to search through.
            Example: {"a": ["ATP", "NADH"], "b": ["FAD"], "c": ["atp",
            "CoA"]}
        search_value (str): The value to search for in the dictionary
        values.
            Example: "atp"

    Returns:
        list: A list of keys whose values (lowercased) contain the
        lowercase search_value.
            Example output: ["a", "c"]
    """
    keys_found = []
    # Convert search_value to lowercase once
    search_value_lower = str(search_value).lower()

    for key, values in data_dict.items():
        # Convert all values to lowercase strings for comparison
        lowercased_values = [str(v).lower() for v in values]

        if search_value_lower in lowercased_values:
            keys_found.append(key)

    return keys_found



def find_matching_dict(dic_tsv_results: list, target: str):
    """
    Returns the first dictionary from dic_tsv_results where the
    'Metabolites' field contains the target string, either directly or
    split by ' _AND_ '.

    Args:
        dic_tsv_results (list): List of dictionaries containing a
        'Metabolites' key.
        target (str): The target metabolite name to search for
        (case-insensitive).

    Returns:
        dict or None: The first matching dictionary or None if no match
        is found.
    """
    target = target.strip().lower()

    for entry in dic_tsv_results:
        # Get the 'Metabolites' value and handle missing or non-string cases
        raw_value = entry.get("Metabolites")
        if not isinstance(raw_value, str):
            continue

        # Split if ' _AND_ ' is present, otherwise just use the raw value
        values = [val.strip().lower() for val in raw_value.split(" _AND_ ")]

        if target in values:
            return entry

    return None




def find_matching_dict_all_key(dic_tsv_results: list, target: str):
    """
    Search for the first dictionary in dic_tsv_results where any
    relevant field contains the target string (case-insensitive),
    including:
    - 'Metabolites' (split by ' _AND_ ')
    - 'Match in database'
    - 'Partial match' (if present, also split by ' _AND_ ')

    Args:
        dic_tsv_results (list): List of dictionaries with
        metabolite-related keys.
        target (str): The target metabolite name to search for.

    Returns:
        dict or None: The first matching dictionary or None if no match
        is found.
    """
    target = target.strip().lower()
    keys_to_check = ["Metabolites", "Match in database", "Partial match"]

    for entry in dic_tsv_results:
        for key in keys_to_check:
            if key not in entry:
                continue  # Skip if key not present

            value = entry[key]
            if not isinstance(value, str) or not value.strip():
                continue  # Skip if value is not a valid non-empty string

            # Split on ' _AND_ ' if needed
            values = (
                [v.strip().lower() for v in value.split(" _AND_ ")]
                if " _AND_ " in value
                else [value.strip().lower()]
            )

            if target in values:
                return entry

    return None


def find_all_entries_with_value(data: list, target_value: str):
    """
    Search through a list of dictionaries and return a list of all
    dictionaries where any value matches the target_value
    (case-insensitive). Values can be strings or lists/tuples of
    strings.

    Args:
        data (list): List of dictionaries to search.
        target_value (str): The value to look for (case-insensitive).

    Returns:
        list: List of dictionaries containing the target_value. Empty
        list if none found.
    """
    target_value_lower = target_value.lower()
    matched_entries = []

    for entry in data:
        for val in entry.values():
            if isinstance(val, str):
                if val.lower() == target_value_lower:
                    matched_entries.append(entry)
                    break  # No need to check other values in this dict
            elif isinstance(val, (list, tuple)):
                if any(
                    isinstance(item, str) and item.lower() == target_value_lower
                    for item in val
                ):
                    matched_entries.append(entry)
                    break  # Stop checking this dict once a match is found

    return matched_entries


def find_all_entries_with_value_tsv(data: list, target_value: str):
    """
    Search through a list of dictionaries and return a list of all
    dictionaries where any key or value matches the target_value
    (case-insensitive). Values can be strings or lists/tuples of
    strings. If a string contains ' _AND_ ', split it and check each
    part.

    Args:
        data (list): List of dictionaries to search.
        target_value (str): The value to look for (case-insensitive).

    Returns:
        list: List of dictionaries containing the target_value in any
        key or value. Empty list if none found.
    """
    target_value_lower = target_value.lower()
    matched_entries = []

    def check_string(s):
        # Split on ' _AND_' and check each part
        parts = [part.strip() for part in s.split(" _AND_ ")]
        return any(part.lower() == target_value_lower for part in parts)

    for entry in data:
        # Check keys
        if any(check_string(str(k)) for k in entry.keys()):
            matched_entries.append(entry)
            continue  # Already matched, skip values

        # Check values
        for val in entry.values():
            if isinstance(val, str):
                if check_string(val):
                    matched_entries.append(entry)
                    break
            elif isinstance(val, (list, tuple)):
                # Check each item, which should be a string
                if any(isinstance(item, str) and check_string(item) for item in val):
                    matched_entries.append(entry)
                    break

    return matched_entries


def find_key_by_list_value(data: dict, search_value: str):
    """
    Searches for a value inside the lists of a dictionary.
    Returns the key whose list contains the value (case-insensitive).

    Args:
        data (dict): Dictionary with list values.
        search_value (str): Value to search for (case-insensitive).

    Returns:
        str or None: The key where the value is found, or None.
    """
    return next(
        (
            k
            for k, v in data.items()
            if isinstance(v, list)
            and any(
                isinstance(el, str) and el.lower() == search_value.lower() for el in v
            )
        ),
        None,
    )


def check_formula_in_dict(data: dict, target_formula: str) -> bool:
    """
    Check if the 'formula' key exists in the dictionary and if any of
    its values matches the target_formula (case-insensitive).
    Args:
        data (dict): The dictionary to check. Expected to have a
        'formula' key with a list of strings.
        target_formula (str): The formula string to compare against.
    Returns:
        bool: True if target_formula matches any value in the 'formula'
        list (case-insensitive), else False.
    """
    # Get the value associated with 'formula' key; default to empty list if not present.
    formula_values = data.get("formula", [])
    # Make sure formula_values is iterable (like a list).
    if not isinstance(formula_values, (list, tuple)):
        return False
    # Compare each formula string in the list to the target_formula, ignoring case.
    for formula in formula_values:
        if isinstance(formula, str) and formula.lower() == target_formula.lower():
            return True
    # No match found.
    return False


# Unmatch filtering
def normalize_cell(cell):
    """
    Normalize the content of a cell into a list of lowercase string
    values.

    - If the cell is a string representing a list, it is parsed using
      `ast.literal_eval`.
    - If the cell is a single value, it is returned as a one-element
      list.
    - Empty or NaN values are filtered out.

    Parameters:
        cell (any): The cell content from a DataFrame row.

    Returns:
        list: A list of normalized (lowercased and stripped) string values.
    """
    # Skip NaN for scalars only
    if not isinstance(cell, list) and pd.isna(cell):
        return []

    try:
        # Try to parse stringified list
        parsed = ast.literal_eval(cell) if isinstance(cell, str) else cell
        if isinstance(parsed, list):
            return [str(x).strip().lower() for x in parsed if pd.notna(x)]
    except Exception:
        pass

    return [str(cell).strip().lower()]


def process_unmatches(df, match_list, unmatch_list):
    """
    Optimized version using `apply()` to normalize each row,
    then identify rows with both match and unmatch IDs.
    """
    match_set = set(str(x).strip().lower() for x in match_list)
    unmatch_set = set(str(x).strip().lower() for x in unmatch_list)

    to_remove = set()

    def normalize_row(row):
        values = []
        for cell in row:
            values.extend(normalize_cell(cell))
        return set(values)

    # Apply normalization to each row
    normalized_rows = df.apply(normalize_row, axis=1)

    for row_values in normalized_rows:
        if row_values & match_set and row_values & unmatch_set:
            to_remove.update(row_values & unmatch_set)

    # Final unmatched list without conflicted IDs
    return [id_ for id_ in unmatch_list if str(id_).strip().lower() not in to_remove]


# Unmatch harmonisation for outputfile
def normalize_cell_preserve_case(cell):
    """
    Normalize a cell while preserving original casing.
    - If the cell is a string representing a list, parse it.
    - If it's already a list, return its cleaned content.
    - If it's a scalar, return it as a one-element list.
    - Filters out NaNs.
    """
    if not isinstance(cell, list) and pd.isna(cell):
        return []
    try:
        parsed = ast.literal_eval(cell) if isinstance(cell, str) else cell
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if pd.notna(x)]
    except Exception:
        pass
    return [str(cell).strip()]


def extract_metabolite_combinations(metabolites_list, df):
    """
    Extracts combinations (including single hits) of metabolites from
    rows of the DataFrame. Keeps original casing and order from
    DataFrame, but uses lowercase for matching.

    Parameters:
        metabolites_list (list): List of target metabolites (strings).
        df (pd.DataFrame): DataFrame with cells possibly containing
        lists or strings.

    Returns:
        list: A list of strings like 'Glucose_AND_Lactate' or 'Glucose',
              one for each row where at least 1 metabolite was found.
    """
    result = []
    metabolites_set = set(str(m).strip().lower() for m in metabolites_list)

    for _, row in df.iterrows():
        row_values = []
        for cell in row:
            row_values.extend(normalize_cell_preserve_case(cell))

        # Keep original casing and order, but filter by lowercase comparison
        found = [v for v in row_values if v.lower() in metabolites_set]

        if found:
            result.append(" _AND_ ".join(found))

    return result


# _____

# Group of function for the smart merge
"""
This set of functions works together to intelligently merge similar
dictionary entries based on shared values in key fields.
- First, strings containing multiple items separated by _AND_ are split
  and cleaned for accurate comparison.
- Then, a similarity graph is built where each dictionary is a node, and
  edges connect dictionaries sharing common values.
- Connected components (groups) of related dictionaries are identified
  within this graph.
- Finally, each group is merged into a single dictionary by combining
  and organizing their values neatly.
- The top-level function coordinates these steps to return a clean,
  merged list of dictionaries representing grouped and unified data
  entries.
"""


# Splits a complex string into clean individual parts.
def split_and_clean(val):
    """
    Splits a string on '_AND_' and removes surrounding whitespace
    from each part.

    Args:
        val (str): Input string, possibly containing multiple values
        joined by '_AND_'.

    Returns:
        set: A set of cleaned individual values.
    """
    if isinstance(val, str):
        return set(v.strip() for v in val.split("_AND_") if v.strip())
    return set()


# Creates a graph representing relationships between dictionaries based
# on common values.
def build_similarity_graph(dicts, keys_to_check):
    """
    Builds a graph where nodes represent dictionaries and edges indicate
    similarity based on overlapping values in specified keys.

    Args:
        dicts (list of dict): List of dictionaries to compare.
        keys_to_check (list of str): Keys to compare across dictionaries.

    Returns:
        graph (dict): A graph represented as an adjacency list.
    """
    graph = defaultdict(set)
    for i, d1 in enumerate(dicts):
        for j, d2 in enumerate(dicts):
            if i >= j:
                continue
            for key in keys_to_check:
                v1 = split_and_clean(d1.get(key, ""))
                v2 = split_and_clean(d2.get(key, ""))
                if v1 & v2:
                    graph[i].add(j)
                    graph[j].add(i)
                    break
    return graph


# Finds groups of connected dictionaries within the graph.
def get_connected_components(graph, n):
    """Extracts connected components (groups) from a graph.

    Args:
        graph (dict): Adjacency list of the graph.
        n (int): Total number of nodes (dictionaries).

    Returns:
        merged_results (list of sets): Each set contains indices of
        dictionaries in the same group.
    """
    visited = set()
    components = []

    for i in range(n):
        if i not in visited:
            stack = [i]
            group = set()
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    group.add(node)
                    stack.extend(graph[node])
            components.append(group)
    return components


# Merges a group of dictionaries by properly combining their values.
def merge_dict_group(dicts):
    """
    Merges a group of similar dictionaries into one, combining values
    properly.

    Args:
        dicts (list of dict): List of dictionaries to merge.

    Returns:
        merged (dict): A single merged dictionary.
    """
    merged = {}
    keys = set().union(*[d.keys() for d in dicts])
    all_values_by_key = defaultdict(set)
    all_metabolites = set()

    for d in dicts:
        metab = d.get("Metabolites")
        if metab:
            all_metabolites.update(split_and_clean(metab))

        for key in keys:
            if key == "Metabolites":
                continue
            val = d.get(key)
            if isinstance(val, list):
                all_values_by_key[key].update(val)
            elif isinstance(val, str):
                all_values_by_key[key].update(split_and_clean(val))

    if all_metabolites:
        merged["Metabolites"] = " _AND_ ".join(sorted(all_metabolites))

    for key, values in all_values_by_key.items():
        if key == "Match in metabolic networks":
            merged[key] = list(sorted(values))
        else:
            merged[key] = " _AND_ ".join(sorted(values))

    return merged


# The complete orchestration — identifies groups and then merges them.
def smart_merge(dict_list):
    """
    Groups similar dictionaries based on shared values in key fields,
    then merges them.

    Args:
        dict_list (list of dict): List of dictionaries representing
        metabolic matches.

    Returns:
        merged_results (list of dict): Merged dictionaries, where
        similar entries are combined into one.
    """
    keys_to_compare = ["Metabolites", "Match in database", "Partial match"]
    graph = build_similarity_graph(dict_list, keys_to_compare)
    components = get_connected_components(graph, len(dict_list))

    merged_results = []
    already_seen = set()

    for component in components:
        group = [dict_list[i] for i in component]
        merged = merge_dict_group(group)
        merged_results.append(merged)
        already_seen.update(component)

    for i in range(len(dict_list)):
        if i not in already_seen:
            merged_results.append(dict_list[i])

    return merged_results
