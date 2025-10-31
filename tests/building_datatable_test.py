#!/bin/python
## MISTIC Project INRIA/INRAE
## Author Muller Coralie
## Date: 2025/08/19
## Update: 2025/10/31

"""
Description:
Test build datatable function for Metacyc and MetNetX mode
"""
from os import path
import pytest
from pathlib import Path
import csv
import os
import tempfile
import json
import pandas as pd
from argparse import Namespace
from metanetmap import build_database
from unittest.mock import patch



#------------------------------------#
#        DIRECTORIES AND FILES       #
#------------------------------------#
TEST_TOYS_DIR = Path(__file__).parent.parent

DATATABLE_COMPLEMENT_METACYC = path.join(TEST_TOYS_DIR,'src/metanetmap/build_datatable_conversion/datatable_complementary_metacyc.tsv')
DATATABLE_COMPLEMENT_METANETX = path.join(TEST_TOYS_DIR,'src/metanetmap/build_datatable_conversion/datatable_complementary_metanetx.tsv')
TEST_EXPECTED_DIR = Path(__file__).parent

# ----------------------------------------------------------

#utils
def read_tsv(fp):
    with open(fp, encoding='utf-8') as f:
        return sorted(list(csv.DictReader(f, delimiter='\t')), key=lambda x: str(x))
    

# ----------------------------------------------------------

#-----------------------#
#         TESTS         #
#-----------------------#

@pytest.mark.skipif(
    not os.path.exists("tests/data/compounds_29.dat") or
    not os.path.exists("tests/data/conversion_datatable.tsv"),
    reason="Required test data files are missing"
)
# Main --> Compare the datatable generated to the one expected 
#### Results table
def test_build_datatable_metacyc(tmp_path):
    # 1. Settings
    output_folder = tmp_path
    output_folder.mkdir(parents=True, exist_ok=True) 
    output_path=Path(output_folder,"conversion_datatable.tsv")

    # 2. Load input data
    Metacyc = "tests/data/compounds_29.dat"
    CONVERSION_DATATABLE = "tests/data/conversion_datatable.tsv"

    # 3. Run the build step
    args = Namespace(
        metacyc_file=Metacyc,
        complement_file=DATATABLE_COMPLEMENT_METACYC,
        output=output_path,
        db='metacyc',
        quiet=True,
                )
    build_database.load_args(args)
   
    
    # 4. Check the generated file
    assert output_path.exists(), "Output file not generated"

    # 5.  Compare contents
    actual = read_tsv(output_path)
    expected = read_tsv(CONVERSION_DATATABLE)
    assert actual == expected, "The generated table does not match the expected one"






@pytest.mark.skipif(
    not os.path.exists("tests/data/chem_xref.tsv") or
    not os.path.exists("tests/data/chem_prop.tsv") or
    not os.path.exists("tests/data/metanetx_conversion_datatable.tsv"),
    reason="Required test data files are missing"
)
# Main --> Compare the datatable generated to the one expected 
#### Results table
def test_build_datatable_metanetx(tmp_path):
    # 1. Settings
    output_folder = tmp_path
    output_folder.mkdir(parents=True, exist_ok=True) 
    output_path=Path(output_folder,"conversion_datatable.tsv")

    # 2. Load input data
    chem_prop_file="tests/data/chem_prop.tsv"
    chem_ref_file="tests/data/chem_xref.tsv"
    CONVERSION_DATATABLE_METANETX = "tests/data/metanetx_conversion_datatable.tsv"

    # 3. Run the build step
    args = Namespace(
        chem_prop_file=chem_prop_file,
        chem_ref_file=chem_ref_file,
        complement_file=DATATABLE_COMPLEMENT_METANETX,
        output=output_path,
        db='metanetx',
        quiet=True,
    )
    build_database.load_args(args)

    
    # 3. Check the generated file
    assert output_path.exists(), "Output file not generated"

    # 4.  Compare contents
    actual = read_tsv(output_path)
    expected = read_tsv(CONVERSION_DATATABLE_METANETX)
    assert actual == expected, "The generated table does not match the expected one"




def test_split_line_adds_extracted_value_to_dict():
    # Simulate a binary line from a MetaCyc/MetaNetX file
    line = b'(COMMON-NAME "Glucose")'
    column_name = "COMMON-NAME"
    dictionary_temp = {}

    # Call the function
    build_database.split_line(line, column_name, dictionary_temp)

    # Check if the dictionary was updated correctly
    assert column_name in dictionary_temp
    assert dictionary_temp[column_name] == "Glucose"


def test_replace_header_line_updates_dictionary():
    # Example binary line from a MetaCyc/MetaNetX file header
    line = b'UNIQUE-ID - META00001\n'
    column_name = "UNIQUE-ID"
    dictionary_temp = {}

    # Call the function
    build_database.replace_header_line(line, column_name, dictionary_temp)

    # Assertions
    assert column_name in dictionary_temp
    assert dictionary_temp[column_name] == "META00001"



def test_replace_line_cleans_and_simplifies_text():
    # Example raw MetaCyc/MetaNetX line in bytes
    line = b'COMMON-NAME - <i>D-glucose</i> &rarr; energy\n'

    # Expected cleaned result
    expected = "D-glucose -> energy"

    # Call the function
    result = build_database.replace_line(line)

    # Assertion
    assert result == expected



def test_build_main_dictionary_creates_correct_structure():
    # Create example MetaCyc content as bytes (mock file content)
    content = b"""
UNIQUE-ID - CPD-17659
COMMON-NAME - D-allo-isoleucine
SYNONYMS - isoleucine-allo
ABBREV-NAME - 
MOLECULAR-WEIGHT - 131.17
MONOISOTOPIC-MW - 131.095
DBLINKS - (CHEBI "CHEBI:85306")
DBLINKS - (SEED "C00022")
DBLINKS - (BIGG "bigg_id")
DBLINKS - (HMDB "HMDB0005760"
DBLINKS - (METANETX "MNXM17053")
DBLINKS - (LIGAND-CPD "C21092")
DBLINKS - (REFMET "Lyxose")
DBLINKS - (PUBCHEM "897")
DBLINKS - (CAS "30237-26-4")
INCHI-KEY - InChIKey=AGPKZVBTJJNPAG-CRCLSJGQSA-N
SMILES - CC[C@H](C)[C@@H]([NH3+])C([O-])=O
//
UNIQUE-ID - CPD-12345
COMMON-NAME - glucose
DBLINKS - (CHEBI "CHEBI:12345")

"""

    # Write the content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(content)
        tmpfile_path = tmpfile.name

    # Call the function
    dictionary_db, keys = build_database.build_main_dictionary(tmpfile_path)

    # Clean up the temp file
    os.remove(tmpfile_path)

    # Check the output structure
    assert isinstance(dictionary_db, list)
    assert len(dictionary_db) == 2  # Two metabolites in example

    first_entry = dictionary_db[0]
    assert first_entry['UNIQUE-ID'] == "CPD-17659"
    assert first_entry['CHEBI'] == "CHEBI:85306"  # Assuming split_line strips 'CHEBI:'
    assert 'D-allo-isoleucine' in first_entry['COMMON-NAME']
    assert 'isoleucine-allo' in first_entry['SYNONYMS']
    assert first_entry['MOLECULAR-WEIGHT'] == "131.17"
    assert first_entry['INCHI-KEY'].startswith("InChIKey=")
    assert keys[0] == "UNIQUE-ID"

    second_entry = dictionary_db[1]
    assert second_entry['UNIQUE-ID'] == "CPD-12345"
    assert second_entry['CHEBI'] == "CHEBI:12345"
    assert second_entry['COMMON-NAME'] == "glucose"



def test_manage_synonyms():
    # Input with list of synonyms
    input_data = [
        {'UNIQUE-ID': 'CPD-1', 'SYNONYMS': ["syn1", "syn2"]},
        {'UNIQUE-ID': 'CPD-2', 'SYNONYMS': ""},
        {'UNIQUE-ID': 'CPD-3', 'SYNONYMS': ['single_synonym']},
        {'UNIQUE-ID': 'CPD-4'},  # No SYNONYMS key
    ]
    
    output = build_database.manage_synonyms(input_data)
    
    # Check first entry: list converted to JSON string
    assert isinstance(output[0]['SYNONYMS'], str)
    assert json.loads(output[0]['SYNONYMS']) == ['syn1', 'syn2']

    # Check second entry: None unchanged
    assert output[1]['SYNONYMS'] == ""

    # Check first entry: list converted to JSON string
    assert json.loads(output[2]['SYNONYMS']) == ["single_synonym"]

    # Check fourth entry: no SYNONYMS key remains absent
    assert 'SYNONYMS' not in output[3]


@pytest.mark.parametrize(
    "dictionary_to_add, column_name_add, dictionary_db, expected_output",
    [
        # Test Case 1: Normal case with partial match
        (
            {'CPD-001': 'glc', 'CPD-002': 'pyr'},
            'BIGG',
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'},
                {'UNIQUE-ID': 'CPD-002', 'COMMON-NAME': 'Pyruvate'},
                {'UNIQUE-ID': 'CPD-003', 'COMMON-NAME': 'Lactate'}
            ],
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'BIGG': 'glc'},
                {'UNIQUE-ID': 'CPD-002', 'COMMON-NAME': 'Pyruvate', 'BIGG': 'pyr'},
                {'UNIQUE-ID': 'CPD-003', 'COMMON-NAME': 'Lactate'}
            ]
        ),
        # Test Case 2: No matches
        (
            {'CPD-999': 'x'},
            'SEED',
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'}],
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'},
             {'UNIQUE-ID': 'CPD-999', 'SEED': 'x'}]
        ),
        #Test Case 3: Overwrite existing value
        (
            {'CPD-001': 'new_value'},
            'SEED',
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'SEED': 'old_value'}],
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'SEED': 'new_value'}]
        )
    ]
)
def test_add_each_complement(dictionary_to_add, column_name_add, dictionary_db, expected_output):
    result = build_database.add_each_complement(dictionary_to_add, column_name_add, dictionary_db)
    assert result == expected_output




@pytest.mark.parametrize(
    "dictionary_db, complementary_dicts, expected_output",
    [
        # Test Case 1: Add multiple complementary columns
        (
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'},
                {'UNIQUE-ID': 'CPD-002', 'COMMON-NAME': 'Pyruvate'}
            ],
            {
                'BIGG': {'CPD-001': 'glc', 'CPD-002': 'pyr'},
                'SEED': {'CPD-001': 'cpd00027', 'CPD-002': 'cpd00020'},
                'FORMULA':{'CPD-001': 'C8H6R1N10'}
            },
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'BIGG': 'glc', 'SEED': 'cpd00027','FORMULA': "C8H6R1N10" },
                {'UNIQUE-ID': 'CPD-002', 'COMMON-NAME': 'Pyruvate', 'BIGG': 'pyr', 'SEED': 'cpd00020'}
            ]
        ),

        # Test Case 2: Some IDs in complementary_dicts not in dictionary_db
        (
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'}
            ],
            {
                'BIGG': {'CPD-001': 'glc', 'CPD-999': 'x'},  # CPD-999 ignored
                'SEED': {'CPD-001': 'cpd00027'}
            },
            [
                {'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'BIGG': 'glc', 'SEED': 'cpd00027'},
                {'UNIQUE-ID': 'CPD-999', 'BIGG': 'x'}
            ]
        ),

        # Test Case 3: Empty complementary_dicts (no updates)
        (
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'}],
            {},
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose'}]
        ),

        # Test Case 4: Overwrite existing field
        (
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'SEED': 'old_value'}],
            {'SEED': {'CPD-001': 'new_value'}},
            [{'UNIQUE-ID': 'CPD-001', 'COMMON-NAME': 'Glucose', 'SEED': 'new_value'}]
        )
    ]
)
def test_add_complement_from_complementary(dictionary_db, complementary_dicts, expected_output):
    result = build_database.add_complement_from_complementary(dictionary_db, complementary_dicts)
    assert result == expected_output


# Test load complement:
#Helper to write a TSV file
def create_temp_tsv(headers, rows):
    tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='')
    writer = csv.writer(tmp, delimiter='\t')
    writer.writerow(headers)
    writer.writerows(rows)
    tmp.close()
    return tmp.name


#Parametrized test for successful and partial data loads
@pytest.mark.parametrize("headers, rows, expected", [
    (
        ['UNIQUE-ID', 'BIGG', 'SEED'],
        [['CPD-123', 'glc', 'cpd00027'], ['CPD-456', 'pyr', 'cpd00020']],
        {
            'BIGG': {'CPD-123': 'glc', 'CPD-456': 'pyr'},
            'SEED': {'CPD-123': 'cpd00027', 'CPD-456': 'cpd00020'}
        }
    ),
    (
        ['UNIQUE-ID', 'BIGG', 'SEED'],
        [['CPD-123', '', 'cpd00027'], ['CPD-456', 'pyr', '']],
        {
            'BIGG': {'CPD-456': 'pyr'},
            'SEED': {'CPD-123': 'cpd00027'}
        }
    )
])
def test_load_complementary_datatable_success(headers, rows, expected):
    path = create_temp_tsv(headers, rows)
    try:
        result = build_database.load_complementary_datatable(path)
        assert result == expected
    finally:
        os.remove(path)


#Grouped error tests
def test_load_complementary_datatable_errors(monkeypatch):
    # File not found
    with pytest.raises(FileNotFoundError):
        build_database.load_complementary_datatable("nonexistent.tsv")

    # Missing UNIQUE-ID
    path2 = create_temp_tsv(['BIGG', 'SEED'], [['glc', 'cpd00027']])
    try:
        with pytest.raises(OSError, match="Missing 'UNIQUE-ID'"):
            build_database.load_complementary_datatable(path2)
    finally:
        os.remove(path2)


############################################ 
#   Build_data test specific to MetaNetX   #
############################################ 


#Test download
def test_download_metanetx_file_success():
    """Test a successful download using a mock."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "test_file.tsv"
        url = "http://example.com/test_file.tsv"

        # Mock urllib.request.urlretrieve to just create an empty file
        def fake_urlretrieve(u, fpath):
            with open(fpath, "w") as f:
                f.write("mock content")
            return (fpath, None)

        with patch("urllib.request.urlretrieve", side_effect=fake_urlretrieve):
            result = build_database.download_metanetx_file(filename, url, tmpdir)

        assert result is not None
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert content == "mock content"

def test_download_metanetx_file_fail():
    """Test download failure returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "test_file.tsv"
        url = "http://example.com/test_file.tsv"

        # Mock urllib.request.urlretrieve to raise an exception
        with patch("urllib.request.urlretrieve", side_effect=Exception("Failed")):
            result = build_database.download_metanetx_file(filename, url, tmpdir)

        assert result is None



# Check reads files
def test_read_chem_prop_basic():
    """Test reading a small chem_prop.tsv content."""
    content = """MNXM1\tGlucose\tRef1\tC6H12O6\t0\t180.16\tInChI1\tKey1\tSMILES1
MNXM2\tATP\tRef2\tC10H16N5O13P3\t-4\t507.18\tInChI2\tKey2\tSMILES2
"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
        tmp.write(content)
        tmp.flush()
        df = build_database.read_chem_prop(tmp.name)
    
    assert df.shape[0] == 2
    assert list(df.columns) == ["MNX_ID","COMMON_NAME","REFERENCE","FORMULA","CHARGE","MOLECULAR_WEIGHT","INCHI","INCHI_KEY","SMILES"]
    assert df.iloc[0]["COMMON_NAME"] == "Glucose"


def test_read_chem_xref_basic():
    """Test reading a small chem_xref.tsv content."""
    content = """chebi:1234\tMNXM1\tGlucose
seed:cpd00001\tMNXM2\tATP
"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
        tmp.write(content)
        tmp.flush()
        df = build_database.read_chem_xref(tmp.name)
    
    assert df.shape[0] == 2
    assert list(df.columns) == ["source","MNX_ID","description"]
    assert df.iloc[1]["source"] == "seed:cpd00001"


# extract ids 

def test_extract_ids_basic():
    """Basic test: extract and group database-specific IDs."""
    df = pd.DataFrame({
        "MNX_ID": ["MNXM1", "MNXM1", "MNXM2", "MNXM3"],
        "source": ["chebi:1234", "chebi:5678", "chebi:9999", "seed:0001"]
    })
    
    result = build_database.extract_ids(df, "chebi")
    
    expected = pd.DataFrame({
        "MNX_ID": ["MNXM1", "MNXM2"],
        "CHEBI": ["chebi:1234|chebi:5678", "chebi:9999"]
    })
    
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_extract_ids_duplicates():
    """Duplicate IDs should be deduplicated and sorted."""
    df = pd.DataFrame({
        "MNX_ID": ["MNXM1", "MNXM1", "MNXM1"],
        "source": ["chebi:2", "chebi:1", "chebi:2"]
    })
    
    result = build_database.extract_ids(df, "chebi")
    expected = pd.DataFrame({
        "MNX_ID": ["MNXM1"],
        "CHEBI": ["chebi:1|chebi:2"]
    })
    
    pd.testing.assert_frame_equal(result, expected)

def test_extract_ids_mixed_prefixes():
    """Only rows with the correct prefix should be extracted."""
    df = pd.DataFrame({
        "MNX_ID": ["MNXM1", "MNXM1", "MNXM2"],
        "source": ["chebi:123", "hmdb:456", "chebi:789"]
    })
    
    result = build_database.extract_ids(df, "chebi")
    expected = pd.DataFrame({
        "MNX_ID": ["MNXM1", "MNXM2"],
        "CHEBI": ["chebi:123", "chebi:789"]
    })
    
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)




# Explode test 
def test_explode_basic():
    """Basic test: explode a column with '|' separators."""
    df = pd.DataFrame({
        "id": [1, 2],
        "metabolite": ["A|B|C", "D"]
    })
    
    result = build_database.explode_ids(df, "metabolite")
    
    expected = pd.DataFrame({
        "id": [1, 1, 1, 2],
        "metabolite": ["A", "B", "C", "D"]
    })
    
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_explode_ignore_empty():
    """Empty strings or spaces should be ignored."""
    df = pd.DataFrame({
        "id": [1],
        "metabolite": ["A||B| |C|"]
    })
    
    result = build_database.explode_ids(df, "metabolite")
    
    expected = pd.DataFrame({
        "id": [1, 1, 1],
        "metabolite": ["A", "B", "C"]
    })
    
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_explode_empty_dataframe():
    """If the input DataFrame is empty, result should be empty."""
    df = pd.DataFrame(columns=["id", "metabolite"])
    result = build_database.explode_ids(df, "metabolite")
    assert result.empty

def test_explode_single_value():
    """If the column has a single value with no separator, it should remain unchanged."""
    df = pd.DataFrame({"id": [1], "metabolite": ["X"]})
    result = build_database.explode_ids(df, "metabolite")
    expected = pd.DataFrame({"id": [1], "metabolite": ["X"]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_explode_with_duplicates():
    """Duplicate values should be preserved unless explicitly removed."""
    df = pd.DataFrame({"id": [1], "metabolite": ["A|A|B"]})
    result = build_database.explode_ids(df, "metabolite")
    expected = pd.DataFrame({
        "id": [1, 1, 1],
        "metabolite": ["A", "A", "B"]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


# Simply test 
@pytest.mark.parametrize("func,val,expected", [
    # BiGG
    (build_database.simplify_bigg, "bigg.metabolite:glc__D", "glc__D"),
    (build_database.simplify_bigg, "biggM:M_glc__D", "glc__D"),
    (build_database.simplify_bigg, "M_atp|biggM:M_adp|biggM:Pi", "Pi|adp|atp"),
    (build_database.simplify_bigg, None, ""),
    
    # SEED
    (build_database.simplify_seed, "seed.compound:cpd00001", "cpd00001"),
    (build_database.simplify_seed, "M_cpd00002|seedM:cpd00003", "cpd00002|cpd00003"),
    (build_database.simplify_seed, "", ""),
    
    # VMH
    (build_database.simplify_vmh, "vmhM:M_oh1|vmhM:oh1|vmhmetabolite:oh1", "oh1"),
    (build_database.simplify_vmh, "M_lac_L", "lac_L"),
    (build_database.simplify_vmh, None, ""),
    
    # HMDB
    (build_database.simplify_hmdb, "hmdb:HMDB0000123", "HMDB0000123"),
    (build_database.simplify_hmdb, "HMDB0000123|HMDB0000456", "HMDB0000123"),
    (build_database.simplify_hmdb, "foo|bar", "bar"),
    (build_database.simplify_hmdb, None, ""),
    
    # MetaCyc
    (build_database.simplify_metacyc, "metacyc.compound:GLC|metacycM:ATP", "ATP|GLC"),
    (build_database.simplify_metacyc, "GLC", "GLC"),
    (build_database.simplify_metacyc, "", ""),
    
    # Remove M_
    (build_database.remove_prefix_M, "M_glc__D|M_atp", "glc__D|atp"),
    (build_database.remove_prefix_M, "", ""),
    (build_database.remove_prefix_M, None, None),
])
def test_simplify_functions(func, val, expected):
    """Generic test for all simplify_* functions."""
    result = func(val)
    assert result == expected