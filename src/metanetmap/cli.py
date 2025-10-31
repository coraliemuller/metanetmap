#!/bin/python
# MISTIC Project INRIA/INRAE
# Author Muller Coralie
# Date: 2025/08/16
# Update: 2025/08/-


import argparse
import datetime
import importlib.resources
import logging
import sys
import time
from argparse import Namespace
from importlib.metadata import version
from pathlib import Path

from metanetmap import mapping, utils
from metanetmap.build_database import load_args

"""Console script for metanetmap."""
VERSION = version("metanetmap")
LICENSE = """Copyright (C) 2024-2027 Coralie Muller, Sylvain Prigent
and Clémence Frioux - Inria (Pleiade) - INRAe (META).
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>"""

MESSAGE = """
Mapping allow matching and unmatching between metabolic networks and
annotation profile of metabolomics.
"""

logger = logging.getLogger("Mapping")


def main():
    # ----------------------#
    #    Begin timer       #
    # ----------------------#
    timestamp = time.time()
    # Convert timestamp to datetime object
    dt = datetime.datetime.fromtimestamp(timestamp)
    # Format the datetime in a readable English format
    start_time = dt.strftime("%Y-%m-%d_%H_%M_%S")
    parser = argparse.ArgumentParser(
        prog="metanetmap",
        description=MESSAGE
        + " For specific help on each subcommand use: mapping {cmd} --help",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + VERSION + "\n" + LICENSE,
    )

    # --------------------#
    #     parent parser  #
    # --------------------#

    # Input SBML directory or file
    parent_parser_sbml = argparse.ArgumentParser(add_help=False)
    parent_parser_sbml.add_argument(
        "-s",
        "--sbml_input",
        help="Path to the directory with SBML files (multiple option)",
        required=True,
    )

    # Input MAF directory or file
    parent_parser_maf = argparse.ArgumentParser(add_help=False)
    parent_parser_maf.add_argument(
        "-a",
        "--maf_input",
        help="Path to the directory with MAF files (.tsv) (multiple option)",
        required=True,
    )

    # Path to database conversion file
    parent_parser_database_conversion = argparse.ArgumentParser(add_help=False)
    parent_parser_database_conversion.add_argument(
        "-d",
        "--database_conversion",
        help="Path to the database conversion file",
        required=True,
    )

    # Multiple complement files for build_db mode
    parent_parser_files_for_build_db = argparse.ArgumentParser(
        add_help=False)
    parent_parser_files_for_build_db.add_argument(
        "-f",
        "--files_for_build_db",
        help="Paths to main files for database conversion (build_db mode)\n"
        "\nExample: -f <path>/compounds_29.dat (Metacyc) OR  <path>/chem_prop.tsv <path>/chem_xref.tsv (MetaNetX)",
        nargs="+",
        required=False,
    )
    # Complementary file
    parent_parser_complement_files_for_build_db = argparse.ArgumentParser(
        add_help=False
    )
    parent_parser_complement_files_for_build_db.add_argument(
        "--compfiles",
        help="Paths to complement files for database conversion (build_db mode)\n"
        "\nExample: -f <path>/complementary_db.tsv",
        required=False,
    )

    # Output path for
    parent_parser_out_db = argparse.ArgumentParser(
        add_help=False
    )
    parent_parser_out_db.add_argument(
        "--out_db",
        help="Path for the creation of the  to complement files for database conversion (build_db mode)\n"
        "\nExample: -f <pathoutput>/",
        required=False,
    )

    # Metacyc or MetaNetX methods
    parent_parser_db = argparse.ArgumentParser(add_help=False)
    parent_parser_db.add_argument(
        "--db",
        help="Choose 'metacyc' or 'metanetx' methods to build the conversion datatable"
        "--db metacyc or --db metanetx"
    )

    # Community mode for test:
    parent_parser_com_for_test = argparse.ArgumentParser(add_help=False)
    parent_parser_com_for_test.add_argument(
        "-c",
        "--community",
        help="Community option for test mode",
        action="store_true",
    )

    # Output folder for mapping results
    parent_parser_output = argparse.ArgumentParser(add_help=False)
    parent_parser_output.add_argument(
        "-o",
        "--output_folder",
        help="Output directory for mapping results",
    )

    # Partial mode (remove enantiomers temporarily)
    parent_parser_partial = argparse.ArgumentParser(add_help=False)
    parent_parser_partial.add_argument(
        "-p", "--partial_match", help="Run the partial match mode ", action="store_true"
    )

    # Quiet mode (less verbose output)
    parent_parser_quiet = argparse.ArgumentParser(add_help=False)
    parent_parser_quiet.add_argument(
        "-q",
        "--quiet",
        help="Enable quiet mode (less verbose output)",
        action="store_true",
    )

    # -----------------#
    #    subparsers
    # -----------------#
    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands:", dest="cmd"
    )

    # Build database mode
    subparsers.add_parser(
        "build_db",
        help="Run in building mode",
        parents=[parent_parser_db,
        parent_parser_files_for_build_db,
        parent_parser_complement_files_for_build_db,
        parent_parser_out_db,
        parent_parser_quiet,
                ],
        description="Run database building mode to generate the "
        "database conversion file",
    )

    # Classic mode
    subparsers.add_parser(
        "classic",
        help="Run in classic mode ",
        parents=[
            parent_parser_sbml,
            parent_parser_maf,
            parent_parser_database_conversion,
            parent_parser_partial,
            parent_parser_quiet,
            parent_parser_output,
        ],
        description="Run in classic mode, with one metabolomic file "
        "and many metabolomic networks",
    )

    # Community mode
    subparsers.add_parser(
        "community",
        help="Run in community mode ",
        parents=[
            parent_parser_sbml,
            parent_parser_maf,
            parent_parser_database_conversion,
            parent_parser_partial,
            parent_parser_quiet,
            parent_parser_output,
        ],
        description="Run in community mode, with many metabolomic "
        "files and metabolic networks files",
    )

    # Test mode
    subparsers.add_parser(
        "test",
        help="Run in community mode ",
        parents=[
            parent_parser_quiet,
            parent_parser_partial,
            parent_parser_com_for_test,
        ],
        description="Run in test mode, with toys files",
    )

    args = parser.parse_args()

    # If no argument print the help.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # -------------------------------#
    #       Set up the logger       #
    # -------------------------------#

    logger = utils.setup_full_logger(args, start_time)

    # ----------------------------------------#
    #      Check version  main package       #
    # ----------------------------------------#
    if args.cmd != "build_db":
        logger.info("-----------------------------------------")
        logger.info("            MAPPING METABOLITES ")
        logger.info("----------------------------------------- \n")
        logger.info("------> Main package version <------")
        packages_to_check = ["numpy", "pandas", "cobra"]
        utils.log_package_versions(packages_to_check)
        logger.info("\nCommand run:")
        logger.info("Actual command run (from sys.argv): python " + " ".join(sys.argv))
        logger.info("\n")

    # #----------------------------------------#
    # #      Set ARGS and General parameters   #
    # #----------------------------------------#
    if args.cmd != "build_db" and args.cmd != "test":
        database_conversion = args.database_conversion
        sbml_input = args.sbml_input
        maf_input = args.maf_input
        utils.is_valid_path(args.sbml_input)
        utils.is_valid_path(args.maf_input)
        utils.is_valid_file(args.database_conversion)
    List_MAF_paths = []
    List_SBML_paths = []

    # #----------------------------------------#
    # #        Check validity of paths         #
    # #----------------------------------------#

    if args.cmd != "test" and args.cmd != "build_db":
        if args.output_folder:
            utils.is_valid_dir(args.output_folder)
            output_folder = args.output_folder
        if not args.output_folder:
            USER_DIR = Path.cwd()
            utils.is_valid_dir(USER_DIR / "mapping/")
            output_folder = USER_DIR / "mapping/"

    # #----------------------------------------#
    # #   Load the database convertion table   #
    # #----------------------------------------#
    if args.cmd != "test" and args.cmd != "build_db":
        if args.database_conversion:
            dictionary_db = mapping.load_database(database_conversion)
    else:
        database_conversion = importlib.resources.files(
            "metanetmap.toys_tests_data"
        ).joinpath("conversion_datatable_toys.tsv")
        dictionary_db = mapping.load_database(database_conversion)

    # #----------------------#
    # #    Main command      #
    # #----------------------#
    if args.cmd == "build_db":
        if args.db == "metacyc":
            files_for_build_db = args.files_for_build_db
            if len(files_for_build_db) != 1:
                logger.critical(
                    "Error: the required 'metacyc' file is missing. "
                    "Please check that the specified path is correct: "
                    "-f <path>/bases/metacyc/compounds_29.dat"
                )
                sys.exit()
            else:
                utils.is_valid_file(files_for_build_db[0])
                args = Namespace(
                    metacyc_file=files_for_build_db[0],
                    complement_file=args.compfiles,
                    output=args.out_db,
                    db=args.db,
                    quiet=args.quiet,
                )
                load_args(args)
        elif args.db == "metanetx":
            if not args.files_for_build_db:
                files_for_build_db = [ "",""]
            else:
                files_for_build_db = args.files_for_build_db
            args = Namespace(
                chem_prop_file=files_for_build_db[0],
                chem_ref_file=files_for_build_db[1],
                complement_file=args.compfiles,
                output=args.out_db,
                db=args.db,
                quiet=args.quiet,
            )
            load_args(args)
        else:
            logger.critical(
            "Error: the '--db' argument must be either 'metacyc' or 'metanetx'. "
            "You must choose one of these database methods."
            )
            sys.exit()    

    elif args.cmd == "test":
        #     ## Test toys
        # --- Ressources dans le package ---
        path_sbml_toys1 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.sbml"
        ).joinpath("toys1.sbml")
        path_sbml_toys2 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.sbml"
        ).joinpath("toys2.sbml")
        path_sbml_toys3 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.sbml"
        ).joinpath("toys3.xml")
        path_maf_toys1 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.maf"
        ).joinpath("toys1.tsv")
        path_maf_toys2 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.maf"
        ).joinpath("toys2.tsv")
        path_maf_toys3 = importlib.resources.files(
            "metanetmap.toys_tests_data.toys.maf"
        ).joinpath("toys3.tsv")

        USER_DIR = Path.cwd()
        output_folder_community = USER_DIR / "toys/"
        output_folder_classic = USER_DIR / "toys/"

        utils.is_valid_dir(output_folder_community)
        utils.is_valid_dir(output_folder_classic)

        if args.community:
            # TEST MAPPING ---> COMMUNITY MODE
            logger.info("#---------------------------#")
            logger.info("      Test COMMUNITY   ")
            logger.info("#---------------------------#")
            logger.info("")

            List_MAF_paths = [path_maf_toys1, path_maf_toys3, path_maf_toys2]
            List_SBML_paths = [path_sbml_toys1, path_sbml_toys3, path_sbml_toys2]

            maf_dictionnary, keys, maf_df = mapping.setup_merged_list_maf_metabolites(
                List_MAF_paths
            )
            dic_couple_sbml, meta_data_sbml = mapping.setup_merge_list_sbml_metabolites(
                List_SBML_paths
            )
            mapping.mapping_run(
                output_folder_community,
                dictionary_db,
                maf_dictionnary,
                keys,
                maf_df,
                meta_data_sbml,
                dic_couple_sbml,
                start_time,
                args.partial_match,
                args.quiet,
                timestamp,
                "community",
            )
            logger.info("#---------------------------#")
            logger.info("      Done: Community   ")
            logger.info("#---------------------------#")
            logger.info(
                "\n--- Total runtime %.2f seconds ---\n ---> MAPPING TEST COMPLETED"
                % (time.time() - timestamp)
            )

        else:
            # TEST MAPPING ---> CLASSIC MODE
            logger.info("#---------------------------#")
            logger.info("      Test CLASSIC   ")
            logger.info("#---------------------------#")
            logger.info("")
            logger.info("")
            List_SBML_paths = mapping.set_list_paths(
                path_sbml_toys2, List_SBML_paths, ".sbml", ".xml"
            )
            List_MAF_paths = [path_maf_toys1, path_maf_toys2, path_maf_toys3]

            maf_dictionnary, keys, maf_df = mapping.setup_merged_list_maf_metabolites(
                List_MAF_paths
            )
            dic_couple_sbml, meta_data_sbml = mapping.setup_merge_list_sbml_metabolites(
                List_SBML_paths
            )
            mapping.mapping_run(
                output_folder_classic,
                dictionary_db,
                maf_dictionnary,
                keys,
                maf_df,
                meta_data_sbml,
                dic_couple_sbml,
                start_time,
                args.partial_match,
                args.quiet,
                timestamp,
                choice=None,
            )

            logger.info("\n#---------------------------#")
            logger.info("      Done: Classic   ")
            logger.info("#---------------------------#")
            logger.info(
                "\n--- Total runtime %.2f seconds ---\n ---> MAPPING COMPLETED'"
                % (time.time() - timestamp)
            )

    elif args.cmd == "community":
        if args.database_conversion and args.maf_input and args.sbml_input:
            logger.info("---->    MODE COMMUNITY    <----")
            logger.info(
                f"Load metabolomics data user path: {maf_input} and "
                f"metabolic networks user path: {sbml_input}\n"
            )

            if Path(sbml_input).is_dir() and Path(maf_input).is_dir():
                List_MAF_paths = mapping.set_list_paths(
                    maf_input, List_MAF_paths, ext1=None, ext2=None
                )
                List_SBML_paths = mapping.set_list_paths(
                    sbml_input, List_SBML_paths, ".sbml", ".xml"
                )

                logger.info("---------------PATHS-------------------")
                logger.info(
                    f"List metabolomics data paths: {List_MAF_paths}\n"
                    f"List metabolic networks paths: {List_SBML_paths}"
                )
                maf_dictionnary, keys, maf_df = (
                    mapping.setup_merged_list_maf_metabolites(List_MAF_paths)
                )
                dic_couple_sbml, meta_data_sbml = (
                    mapping.setup_merge_list_sbml_metabolites(List_SBML_paths)
                )
                mapping.mapping_run(
                    output_folder,
                    dictionary_db,
                    maf_dictionnary,
                    keys,
                    maf_df,
                    meta_data_sbml,
                    dic_couple_sbml,
                    start_time,
                    args.partial_match,
                    args.quiet,
                    timestamp,
                    "community",
                )

                logger.info(
                    "\n--- Total runtime %.2f seconds ---\n ---> MAPPING COMPLETED'"
                    % (time.time() - timestamp)
                )

            else:
                logger.critical(
                    "Error: Paths must be: sbml -> directory, "
                    "maf-> directory \n"
                    f"Check--> Metabolic network: {sbml_input} or "
                    f"metabolomic file: {maf_input}"
                )
                sys.exit()
        else:
            logger.critical(
                "Error: One or multiple paths for mapping in "
                "community mode is/are empty."
            )

    elif args.cmd == "classic":
        if args.database_conversion and args.maf_input and args.sbml_input:
            logger.info(
                "\n---->    MODE CLASSIC    <----       \n\n"
                f"Load metabolomics data user path: {maf_input} and "
                f"metabolic networks user path: {sbml_input}\n"
            )
            if (
                (Path(maf_input).is_file()
                or Path(maf_input).is_dir())
                and Path(sbml_input).is_file()
            ):
                List_MAF_paths = mapping.set_list_paths(
                    maf_input, List_MAF_paths, ext1=None, ext2=None
                )
                List_SBML_paths = mapping.set_list_paths(
                    sbml_input, List_SBML_paths, ".sbml", ".xml"
                )

                logger.info(
                    "\n---------------PATHS-------------------\n"
                    "List metabolomics data paths: %s\n"
                    "List metabolic networks paths: %s\n",
                    List_MAF_paths,
                    List_SBML_paths,
                )

                maf_dictionnary, keys, maf_df = (
                    mapping.setup_merged_list_maf_metabolites(List_MAF_paths)
                )
                dic_couple_sbml, meta_data_sbml = (
                    mapping.setup_merge_list_sbml_metabolites(List_SBML_paths)
                )
                mapping.mapping_run(
                    output_folder,
                    dictionary_db,
                    maf_dictionnary,
                    keys,
                    maf_df,
                    meta_data_sbml,
                    dic_couple_sbml,
                    start_time,
                    args.partial_match,
                    args.quiet,
                    timestamp,
                    choice=None,
                )
                logger.info(
                    "\n--- Total runtime %.2f seconds ---\n ---> MAPPING COMPLETED'"
                    % (time.time() - timestamp)
                )
            else:
                logger.critical(
                    "Error: Paths must be: sbml -> directory, maf-> 1 "
                    "file  \nCheck--> Metabolic network: %s "
                    "or metabolomic file: %s",
                    sbml_input,
                    maf_input,
                )
                sys.exit()
        else:
            logger.critical(
                "Error: One or multiple paths for mapping in classic "
                "mode is/are empty."
            )
