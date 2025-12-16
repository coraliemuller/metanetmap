#!/bin/python
## MISTIC Project INRIA/INRAE
## Author Muller Coralie
## Date: 2025/08/20
## Update: 2025/12/15

"""
Description:
Test preprocess before the matching part
"""
from os import path
import pytest
from pathlib import Path
import ast
import csv
import pandas as pd
from cobra import Model, Metabolite
import cobra.io
import tempfile


from metanetmap import mapping

# /!\ INFO:

# ------------------------------------#
#        DIRECTORIES AND FILES       #
# ------------------------------------#
TEST_TOYS_DIR = Path(__file__).parent.parent
DATATABLE_CONVERSION = path.join(
    TEST_TOYS_DIR, "src/metanetmap/toys_tests_data/conversion_datatable_toys.tsv"
)


# ---------------------------------#
#        EXPECTED SOLUTIONS       #
# ---------------------------------#


### Datatable conversion
def read_expected_table(path: Path):
    expected = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # Convertir la chaîne SYNONYMS en vraie liste
            if "SYNONYMS" in row and row["SYNONYMS"]:
                try:
                    row["SYNONYMS"] = ast.literal_eval(row["SYNONYMS"])
                except Exception:
                    row["SYNONYMS"] = []
            # Format CHEBI
            chebi = row.get("CHEBI")
            if chebi:
                row["CHEBI"] = f"CHEBI:{chebi}"
            # Format PUBCHEM
            pubchem = row.get("PUBCHEM")
            if pubchem:
                row["PUBCHEM"] = f"PUBCHEM:{pubchem}"
            expected.append(row)
    return expected


# ----------------------------------------------------------
# Create mock maf files for test
@pytest.fixture
def mock_maf_files():
    """Creates two temporary MAF (TSV) files for testing."""
    maf_content_1 = "UNIQUE-ID\tCHEBI\tSMILES\nC001\tCHEBI:12345\tC(CO)O\nC002\tCHEBI:67890\tCC(=O)O"
    maf_content_2 = "UNIQUE-ID\tCHEBI\tSMILES\nC003\tCHEBI:12345\tC(CO)O"

    tmp_files = []
    for content in [maf_content_1, maf_content_2]:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv", mode="w")
        tmp.write(content)
        tmp.close()
        tmp_files.append(tmp.name)

    yield tmp_files  # Provide the list of file paths to the test

    # Cleanup
    for f in tmp_files:
        Path(f).unlink(missing_ok=True)


# Create mock sbml files for test
@pytest.fixture
def create_mock_sbml_files():
    """Creates two temporary SBML files with simple metabolite content."""
    tmp_files = []

    for idx in range(2):
        model = Model(f"model_{idx}")
        m = Metabolite(
            id=f"glc_{idx}_c", name="Glucose", formula="C6H12O6", compartment="c"
        )
        m.annotation = {"chebi": [f"CHEBI:000{idx+1}"], "hmdb": [f"HMDB0000123{idx+1}"]}

        model.add_metabolites([m])

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
            cobra.io.write_sbml_model(model, tmp.name)
            tmp_files.append(tmp.name)

    yield tmp_files

    # Cleanup
    for file in tmp_files:
        Path(file).unlink(missing_ok=True)


### Datatable conversion
def test_load_database_matches_expected():
    actual = mapping.load_database(DATATABLE_CONVERSION)
    expected = read_expected_table(Path(DATATABLE_CONVERSION))

    assert actual == expected


#### Test add the MNM_ID


@pytest.fixture
def mock_maf_files(tmp_path):
    """Create mock MAF files for testing."""
    file1 = tmp_path / "maf1.tsv"
    file2 = tmp_path / "maf2.tsv"

    df1 = pd.DataFrame(
        {"CHEBI": ["CHEBI:12345", "CHEBI:67890"], "UNIQUE-ID": ["C001", "C002"]}
    )
    df2 = pd.DataFrame({"CHEBI": ["CHEBI:12345"], "UNIQUE-ID": ["C003"]})

    df1.to_csv(file1, sep="\t", index=False)
    df2.to_csv(file2, sep="\t", index=False)

    return [str(file1), str(file2)]


def test_mnm_id_column_in_output(tmp_path, mock_maf_files):
    """Check that MNM_ID column is added in the output files."""
    output_folder = tmp_path

    # Run the function that writes MNM files to output_folder
    mapping.setup_merged_list_maf_metabolites(mock_maf_files, output_folder)

    # List of expected output files
    output_files = [
        output_folder / "MNM_mafs" / f"MNM_{Path(f).name}" for f in mock_maf_files
    ]

    for out_file in output_files:
        assert out_file.exists(), f"Output file {out_file} was not created"

        df = pd.read_csv(out_file, sep="\t")

        # MNM_ID column should exist
        assert "MNM_ID" in df.columns, f"MNM_ID missing in {out_file}"

        # MNM_ID values should not be empty
        assert df["MNM_ID"].notnull().all(), f"MNM_ID column has nulls in {out_file}"

        # MNM_ID values should be strings
        assert all(
            isinstance(val, str) for val in df["MNM_ID"]
        ), f"Non-string MNM_ID values in {out_file}"


# -----------------------#
#   set_list_paths      #
# -----------------------#
def test_directory_with_valid_extensions(tmp_path):
    # Creates files with valid extensions
    file1 = tmp_path / "pathway1.sbml"
    file2 = tmp_path / "pathway2.xml"
    file1.write_text("dummy")
    file2.write_text("dummy")

    result = mapping.set_list_paths(tmp_path, [], ".sbml", ".xml")

    assert len(result) == 2
    assert str(file1) in result
    assert str(file2) in result


def test_single_valid_file(tmp_path):
    file_valid = tmp_path / "pathway.sbml"
    file_valid.write_text("dummy")

    result = mapping.set_list_paths(file_valid, [], ".sbml", ".xml")
    assert len(result) == 1
    assert str(file_valid) in result


def test_file_without_extension_check(tmp_path):
    file = tmp_path / "any_file.any"
    file.write_text("dummy")

    result = mapping.set_list_paths(file, [], None, None)
    assert result == [str(file)]


def test_directory_without_extension_check(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.json"
    file1.write_text("dummy")
    file2.write_text("dummy")

    result = mapping.set_list_paths(tmp_path, [], None, None)
    assert sorted(result) == sorted([str(file1), str(file2)])


# -----------------------#
#     Merge  Data       #
# -----------------------#

# SBML
# def test_setup_merge_list_sbml_metabolites(create_mock_sbml_files):
#     sbml_paths = create_mock_sbml_files

#     dic_couple_sbml, meta_data_sbml = mapping.setup_merge_list_sbml_metabolites(sbml_paths)

#     # 1. Should have two entries (one per SBML file)
#     assert len(dic_couple_sbml) == 2

#     # 2. Each should contain the metabolite ID, even with extra metadata
#     for ids in dic_couple_sbml.values():
#         assert "glc_0" in ids or "glc_1" in ids

#     # 3. Metadata should contain "Glucose" key
#     assert "Glucose" in meta_data_sbml
#     assert "ID" in meta_data_sbml["Glucose"]
#     assert "formula" in meta_data_sbml["Glucose"]
#     assert "chebi" in meta_data_sbml["Glucose"]

#     # 4. Check that duplicate IDs are removed in metadata
#     assert len(set(meta_data_sbml["Glucose"]["ID"])) == len(meta_data_sbml["Glucose"]["ID"])

# def test_setup_merged_list_maf_metabolites(mock_maf_files):
#     maf_dict, keys, merged_df = mapping.setup_merged_list_maf_metabolites(mock_maf_files)

#     assert "CHEBI" in maf_dict
#     assert sorted(maf_dict["CHEBI"]) == ["CHEBI:12345", "CHEBI:67890"] # check duplicates
#     assert keys == ['UNIQUE-ID','CHEBI','COMMON-NAME','ABBREV-NAME','SYNONYMS','ADD-COMPLEMENT','MOLECULAR-WEIGHT','MONOISOTOPIC-MW','SEED','BIGG','HMDB','METANETX','METACYC','LIGAND-CPD','REFMET','PUBCHEM','VMH','CAS','INCHI','NON-STANDARD-INCHI','INCHI-KEY','SMILES','FORMULA'] # check list of key
#     assert merged_df.shape[0] == 3  # C001, C002, C003


@pytest.fixture
def mock_maf_files(tmp_path):
    # Create mock MAF files as CSV/TSV in a temporary folder
    file1 = tmp_path / "maf1.tsv"
    file2 = tmp_path / "maf2.tsv"

    df1 = pd.DataFrame(
        {"CHEBI": ["CHEBI:12345", "CHEBI:67890"], "UNIQUE-ID": ["C001", "C002"]}
    )
    df2 = pd.DataFrame(
        {"CHEBI": ["CHEBI:12345"], "UNIQUE-ID": ["C003"]}  # duplicate to test merge
    )

    df1.to_csv(file1, sep="\t", index=False)
    df2.to_csv(file2, sep="\t", index=False)

    return [str(file1), str(file2)]  # list of file paths


def test_setup_merged_list_maf_metabolites(mock_maf_files, tmp_path):
    # Use tmp_path as the output_folder
    output_folder = tmp_path

    maf_dict, keys, merged_df = mapping.setup_merged_list_maf_metabolites(
        mock_maf_files, output_folder
    )

    # 1. Check that CHEBI key exists
    assert "CHEBI" in maf_dict

    # 2. Check that duplicates are removed and sorted
    assert sorted(maf_dict["CHEBI"]) == ["CHEBI:12345", "CHEBI:67890"]

    # 3. Check that keys list matches expected columns
    expected_keys = [
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
    assert keys == expected_keys

    # 4. Check that merged_df has 3 rows (C001, C002, C003)
    assert merged_df.shape[0] == 3

    # 5. Optional: check that merged_df contains expected CHEBI IDs
    for chebi_id in ["CHEBI:12345", "CHEBI:67890"]:
        assert chebi_id in merged_df["CHEBI"].values


# -----------------------#
#   metadata_sbml       #
# -----------------------#
# manage_id
@pytest.mark.parametrize(
    "annotations, expected",
    [
        # Case 1: values in list form with prefixes META
        (
            {
                "chebi": ["CHEBI:12345", "CHEBI:67890"],
                "meta": ["META:00001", "META:00002"],
            },
            {"chebi": ["CHEBI:12345", "CHEBI:67890"], "meta": ["00001", "00002"]},
        ),
        # Case 2: Values in the form of unique strings with prefixes
        (
            {"chebi": "CHEBI:54321", "meta": "META:11111"},
            {"chebi": ["CHEBI:54321"], "meta": ["11111"]},
        ),
        # Case 3: Mixing lists and strings
        (
            {"chebi": ["CHEBI:123", "CHEBI:456"], "meta": "META:789"},
            {"chebi": ["CHEBI:123", "CHEBI:456"], "meta": ["789"]},
        ),
        # Case 4: no prefixes to remove META and add for CHEBI
        (
            {
                "sbo": ["SBO:0000247"],
                "reactome": ["R-ALL-158417", "R-ALL-216667"],
                "chebi": ["CHEBI:123", "CHEBI:456"],
                "meta": "789",
            },
            {
                "sbo": ["SBO:0000247"],
                "reactome": ["R-ALL-158417", "R-ALL-216667"],
                "chebi": ["CHEBI:123", "CHEBI:456"],
                "meta": ["789"],
            },
        ),
    ],
)
def test_manage_id_in_metadata_sbml(annotations, expected):
    tmp_data = {}
    result = mapping.manage_id_in_metadata_sbml(annotations, tmp_data)
    assert result == expected


# merge_doublons
def test_update_meta_data_sbml_adds_unique_entries():
    tmp_data = {"chebi": ["123", "456"], "kegg": ["A", "B"]}

    meta_data_sbml = {"glucose": {"chebi": ["123"], "kegg": []}}  # "123" already prsent

    expected = {
        "glucose": {
            "chebi": ["123", "456"],  # "456" zdded, "123" igignored
            "kegg": ["A", "B"],
        }
    }

    result = mapping.merge_doublons_metadata_sbml(meta_data_sbml, "glucose", tmp_data)
    assert result == expected


def test_update_meta_data_sbml_avoids_duplicates():
    tmp_data = {
        "chebi": ["123", "123", "789"],  # remove duplicates even in the same data
    }

    meta_data_sbml = {"met1": {"chebi": ["123", "456"]}}

    expected = {"met1": {"chebi": ["123", "456", "789"]}}

    result = mapping.merge_doublons_metadata_sbml(meta_data_sbml, "met1", tmp_data)
    assert result == expected


# Extract metadata
def test_extract_metadata_sbml(create_mock_sbml_files):
    # Create a dummy SBML model
    model = cobra.io.read_sbml_model(create_mock_sbml_files[0])

    # Initial metadata dictionary (empty or with partial data)
    meta_data_sbml = {}

    # # Call the function
    updated_meta = mapping.extract_metadata_sbml(model, meta_data_sbml)

    # Assertions
    assert "Glucose" in updated_meta
    assert "ID" in updated_meta["Glucose"]
    assert "formula" in updated_meta["Glucose"]
    assert updated_meta["Glucose"]["ID"] == ["glc_0"]
    assert updated_meta["Glucose"]["formula"] == ["C6H12O6"]
    assert updated_meta["Glucose"]["chebi"] == ["CHEBI:0001"]
    assert updated_meta["Glucose"]["hmdb"] == ["HMDB00001231"]
