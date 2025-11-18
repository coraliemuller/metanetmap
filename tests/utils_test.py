#!/bin/python
## MISTIC Project INRIA/INRAE
## Author Muller Coralie
## Date: 2025/08/19
## Update: 2025/10/31

"""
Description:
Test all the utils finctions
"""
from os import path
import csv
import pandas as pd
import pytest

from metanetmap import utils



#--------------------------------------------------------#
#             UTILS -> File management TEST              #
#--------------------------------------------------------#


def test_is_valid_file_existing(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello")
    assert utils.is_valid_file_or_create(str(file)) is True




def test_is_valid_dir_existing(tmp_path):
    assert utils.is_valid_dir(str(tmp_path)) is True



def test_is_valid_dir_creatable(tmp_path):
    new_dir = tmp_path / "newdir"
    # Directory doesn't exist, so should be created
    result = utils.is_valid_dir(str(new_dir))
    assert result is True
    assert new_dir.is_dir()



def test_is_valid_dir_uncreatable(tmp_path, monkeypatch):
    # Simulate os.makedirs raising OSError
    def raise_oserror(path):
        raise OSError("Cannot create directory")
    
    monkeypatch.setattr("os.makedirs", raise_oserror)
    uncreatable_dir = tmp_path / "cannot_create"
    assert utils.is_valid_dir(str(uncreatable_dir)) is False


    
def test_is_valid_path_existing_writable(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello")
    assert utils.is_valid_path(str(file)) is True



def test_is_valid_path_creatable(tmp_path):
    new_file = tmp_path / "newfile.txt"
    # Should be able to create then delete this file
    assert utils.is_valid_file_or_create(str(new_file)) is True



def test_write_tsv(tmp_path):
    data = [
        {'A': 1, 'B': 2, 'C': 3},
        {'A': 4, 'B': 5, 'C': 6}
    ]
    keys_order = ['B', 'A']
    output_file = tmp_path / "out.tsv"

    utils.write_tsv(data, str(tmp_path), "out.tsv", keys_order,False)

    df = pd.read_csv(output_file, sep="\t")
    assert list(df.columns) == keys_order
    assert df.iloc[0]['B'] == 2



def test_remove_empty_keys():
    d = {'a': 1, 'b': '', 'c': None, 'd': 0, 'e': False, 'f': 'text'}
    cleaned = utils.remove_empty_keys(d)
    assert 'a' in cleaned
    assert 'b' not in cleaned
    assert 'c' not in cleaned
    assert 'd' not in cleaned
    assert 'e' not in cleaned
    assert 'f' in cleaned



def test_write_csv(tmp_path):
    data = [
        {'UNIQUE-ID': 'id1', 'A': 'val1'},
        {'UNIQUE-ID': 'id2', 'B': 'val2'},
        {'UNIQUE-ID': '#comment', 'A': 'skip this'}
    ]
    original_keys = ['UNIQUE-ID', 'A']
    output_file = tmp_path / "out.tsv"

    utils.write_csv(data, str(output_file), original_keys)

    with open(output_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    assert reader.fieldnames == ['UNIQUE-ID', 'A', 'B']
    assert all(row['UNIQUE-ID'] != '#comment' for row in rows)
    assert any(row['UNIQUE-ID'] == 'id1' and row['A'] == 'val1' for row in rows)
    assert any(row['UNIQUE-ID'] == 'id2' and row['B'] == 'val2' for row in rows)




#---------------------------------------------------------#
#             UTILS -> UI management TEST                 #
#---------------------------------------------------------#

def test_analyze_column_matches_basic():
    data = [
        {'Match in database': 'CPD-17381', 'Match in metabolic networks': 'roqD'},
        {'Match in database': '', 'Match in metabolic networks': ''},
        {'Match in database': "", 'Match in metabolic networks': 'C9H16NO5'},
        {'Match in database': 'Gal-13-GlcN-R _AND_ beta-Gal-13-beta-GlcNac-R', 'Match in metabolic networks': ""},
        {'Match in database': 'DIMETHYLMAL-CPD', 'Match in metabolic networks': 'dim'}
    ]

    stats = utils.analyze_column_matches(data, 'Match in database', 'Match in metabolic networks')

    assert stats['both_filled'] == 2    # rows 0 and 4
    assert stats['both_empty'] == 1     # row 1
    assert stats['network_only'] == 1   # row 2
    assert stats['db_only'] == 1        # row 3
    assert stats['network_total_filled'] == 3  # rows 0,2,4
    assert stats['network_empty_total'] == 2   # rows 1,3



def test_analyze_column_matches_with_partial():
    data = [
        {'Match in database': 'CPD-17381', 'Match in metabolic networks': '["toys1"]', 'Partial match': 'roqD and roq'},
        {'Match in database': '', 'Match in metabolic networks': '', 'Partial match': ''},
        {'Match in database': "", 'Match in metabolic networks': '["toys2"]', 'Partial match': 'C9H16NO5'},
        {'Match in database': 'Gal-13-GlcN-R _AND_ beta-Gal-13-beta-GlcNac-R', 'Match in metabolic networks': "", 'Partial match': 'GAL'},
        {'Match in database': 'DIMETHYLMAL-CPD', 'Match in metabolic networks': 'dim', 'Partial match': ''},
        {'Match in database': 'CPD-26454', 'Match in metabolic networks': '', 'Partial match': 'CPD-17257 _AND_ CPD-9247 _AND_ Vaccenate'},
        {'Match in database': '', 'Match in metabolic networks': 'h2d', 'Partial match': ''},
    ]

    stats = utils.analyze_column_matches(data, 'Match in database', 'Match in metabolic networks', 'Partial match')

    assert stats['both_filled'] == 2    # rows 0 and 4
    assert stats['both_empty'] == 1     # row 1
    assert stats['network_only'] == 2   # rows 2 and 6
    assert stats['db_only'] == 2        # rows 3 and 5
    assert stats['network_total_filled'] == 4  # rows 0,2,4,6
    assert stats['network_empty_total'] == 3   # rows 1,3,5

    assert stats['partial_and_metabolic_filled'] == 2  # rows 0,2 (net and partial filled)
    assert stats['db_and_partial_only'] == 2            # rows 3,5 (Match in database and partial only)


#--------------------------------------------------------#
#             UTILS -> Search management  TEST           #
#--------------------------------------------------------#



def test_fix_arrows_in_parentheses():
    text = "A (? B) and C (? D)"
    expected = "A (-> B) and C (-> D)"
    assert utils.fix_arrows_in_parentheses(text) == expected

    # Test no parentheses
    text2 = "No question here"
    assert utils.fix_arrows_in_parentheses(text2) == text2





def test_match_single_result():
    data = {
        'OROTATE': {'ID': ['OROTATE_e', 'OROTATE'], 'formula': ''},
        'Carbamyl-phosphate': {'ID': ['Carbamyl-phosphate_c', 'Carbamyl-phosphate'], 'formula': ''},
    }

    result = utils.find_all_sub_dicts_by_nested_value(data, 'OROTATE')
    assert result == [
        {'ID': ['OROTATE_e', 'OROTATE'], 'formula': ''}
    ]

    result = utils.find_all_sub_dicts_by_nested_value(data, 'carbamyl-phosphate_c')
    assert result == [
        {'ID': ['Carbamyl-phosphate_c', 'Carbamyl-phosphate'], 'formula': ''}
    ]


def test_match_multiple_results():
    data = {
        'A': {'ID': ['X', 'Y'], 'other': ['shared']},
        'B': {'ID': ['shared'], 'formula': ''},
        'C': {'ID': ['not_shared'], 'formula': ''}
    }

    result = utils.find_all_sub_dicts_by_nested_value(data, 'shared')

    assert len(result) == 2
    assert {'ID': ['X', 'Y'], 'other': ['shared']} in result
    assert {'ID': ['shared'], 'formula': ''} in result


def test_match_case_insensitive():
    data = {
        'L-methionine': {'ID': ['MET_e', 'MET', 'MET_c'], 'formula': []}
    }

    result = utils.find_all_sub_dicts_by_nested_value(data, 'met')
    assert result == [{'ID': ['MET_e', 'MET', 'MET_c'], 'formula': []}]

    result = utils.find_all_sub_dicts_by_nested_value(data, 'met_e')
    assert result == [{'ID': ['MET_e', 'MET', 'MET_c'], 'formula': []}]


def test_no_match():
    data = {
        'BIOMASS': {'ID': ['BIOMASS_c', 'BIOMASS'], 'formula': ''}
    }

    result = utils.find_all_sub_dicts_by_nested_value(data, 'NOT_FOUND')
    assert result == []  # empty list for no match


def test_empty_data():
    result = utils.find_all_sub_dicts_by_nested_value({}, 'anything')
    assert result == []



#find_dict_by_metabolite

def test_find_dict_by_metabolite():
    data = [
        {'Metabolites': 'glucose', 'Match in database': 'GLC'},
        {'Metabolites': 'fructose', 'Match in database': 'FRC'},
        {'Metabolites': 'sucrose', 'Match in database': 'SRC'},
    ]

    # Test exact match
    assert utils.find_dict_by_metabolite(data, 'fructose') == {'Metabolites': 'fructose', 'Match in database': 'FRC'}

    # Test no match returns None
    assert utils.find_dict_by_metabolite(data, 'maltose') is None

    # Test it returns the first match only
    data.append({'Metabolites': 'fructose', 'Match in database': 'FRC2'})
    assert utils.find_dict_by_metabolite(data, 'fructose') == {'Metabolites': 'fructose', 'Match in database': 'FRC'}

    # Test when 'Metabolites' key is missing in some dicts
    data_with_missing = [
        {'Name': 'glucose'},
        {'Metabolites': 'fructose', 'Match in database': 'FRC'}
    ]
    assert utils.find_dict_by_metabolite(data_with_missing, 'fructose') == {'Metabolites': 'fructose', 'Match in database': 'FRC'}
    assert utils.find_dict_by_metabolite(data_with_missing, 'glucose') is None




def test_find_keys_with_value_in_dict():
    data = {
        "toys1.sbml": ["ATP", "NADH"],
        "toys2.sbml": ["FAD"],
        "toys3.xml": ["atp", "CoA"],
        "toys4.xml": ["NADPH", "Coa"]
    }

    # Test case-insensitive matching returns multiple keys
    assert sorted(utils.find_keys_with_value_in_dict(data, "atp")) == ["toys1.sbml", "toys3.xml"]

    # Test case-insensitive matching for single key
    assert utils.find_keys_with_value_in_dict(data, "fad") == ["toys2.sbml"]

    # Test no matches returns empty list
    assert utils.find_keys_with_value_in_dict(data, "GTP") == []

    # Test searching for a value with different casing
    assert sorted(utils.find_keys_with_value_in_dict(data, "CoA")) == ["toys3.xml", "toys4.xml"]



def test_find_matching_dict():
    data = [
        {'Metabolites': 'glucose'},
        {'Metabolites': 'fructose _AND_ sucrose'},
        {'Metabolites': 'ATP _AND_ NADH'},
        {'Metabolites': None},  # non-string case
        {'noMetabolites': 'xyz'},  # missing key case
    ]

    # Exact single metabolite match, case-insensitive
    assert utils.find_matching_dict(data, 'Glucose') == {'Metabolites': 'glucose'}

    # Compound metabolites - find sucrose (second in list)
    assert utils.find_matching_dict(data, 'Sucrose') == {'Metabolites': 'fructose _AND_ sucrose'}

    # Compound metabolites - find ATP (first in list)
    assert utils.find_matching_dict(data, 'atp') == {'Metabolites': 'ATP _AND_ NADH'}

    # Non-string 'Metabolites' value should be skipped
    assert utils.find_matching_dict(data, 'xyz') is None

    # Missing 'Metabolites' key should be skipped
    assert utils.find_matching_dict(data, 'anything') is None

    # Target with extra whitespace
    assert utils.find_matching_dict(data, '  fructose  ') == {'Metabolites': 'fructose _AND_ sucrose'}





# find_matching_dict_all_key
@pytest.fixture
def sample_data():
    return [
        {'Metabolites': 'ADENINE _AND_ Guanine', 'Match in database': 'YES', 'Partial match': ''},
        {'Metabolites': 'Thymine', 'Match in database': 'NO', 'Partial match': ''},
        {'Metabolites': 'Uracil', 'Match in database': '', 'Partial match': 'Cytosine _AND_ uracil'},
        {'Match in database': 'YES'},  # No 'Metabolites' or 'Partial match'
    ]

def test_match_found_in_metabolites(sample_data):
    result = utils.find_matching_dict_all_key(sample_data, 'guanine')
    assert result == sample_data[0]

def test_match_found_in_partial_match(sample_data):
    result = utils.find_matching_dict_all_key(sample_data, 'Cytosine')
    assert result == sample_data[2]

def test_match_case_insensitive(sample_data):
    result = utils.find_matching_dict_all_key(sample_data, 'thymine')
    assert result == sample_data[1]

def test_no_match_found(sample_data):
    result = utils.find_matching_dict_all_key(sample_data, 'nonexistent')
    assert result is None




#find_all_entries_with_value
@pytest.fixture
def sample_data2():
    return [
        {'UNIQUE-ID': 'id1', 'COMMON-NAME': 'val1'},
        {'UNIQUE-ID': 'id2', 'SMILE': 'val2'},
        {'UNIQUE-ID': '#comment', 'COMMON-NAME': 'skip this'},  # Can be ignored if necessary
        {'UNIQUE-ID': 'id3', 'SYNOMYMS': ['val3', 'Val4']},
        {'UNIQUE-ID': 'id4', 'SYNOMYMS': ['VAL3']},  # Duplicated for multi-match testing
        {'UNIQUE-ID': 'id5', 'C': None},
    ]

def test_exact_string_match(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "val1")
    assert len(matches) == 1
    assert matches[0]['UNIQUE-ID'] == 'id1'

def test_case_insensitive_match(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "VAL2")
    assert len(matches) == 1
    assert matches[0]['UNIQUE-ID'] == 'id2'

def test_match_in_list(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "val3")
    assert any(entry['UNIQUE-ID'] == 'id3' for entry in matches)

def test_case_insensitive_list_match(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "val4")
    assert len(matches) == 1
    assert matches[0]['UNIQUE-ID'] == 'id3'

def test_multiple_matches(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "val3")
    assert len(matches) == 2
    unique_ids = {entry['UNIQUE-ID'] for entry in matches}
    assert unique_ids == {"id3", "id4"}

def test_no_match(sample_data2):
    matches = utils.find_all_entries_with_value(sample_data2, "xyz")
    assert matches == []



#find_all_entries_with_value_tsv
@pytest.fixture
def sample_data3():
    return [
        {'Metabolites': 'ADENINE _AND_ Guanine', 'Match in database': 'YES', 'Partial match': ''},
        {'Metabolites': 'Thymine', 'Match in database': 'NO', 'Partial match': ''},
        {'Metabolites': 'Uracil', 'Match in database': '', 'Partial match': 'Cytosine _AND_ uracil'},
        {'Match in database': 'YES'},  # Missing 'Metabolites' and 'Partial match'
    ]


def test_match_in_metabolites_with_and(sample_data3):
    matches = utils.find_all_entries_with_value_tsv(sample_data3, "adenine")
    assert len(matches) == 1
    assert "ADENINE _AND_ Guanine" in matches[0].get("Metabolites", "")

def test_case_insensitive_match(sample_data3):
    matches = utils.find_all_entries_with_value_tsv(sample_data3, "guAninE")
    assert len(matches) == 1
    assert matches[0]["Metabolites"].lower().find("guanine".lower()) != -1

def test_match_in_partial_match(sample_data3):
    matches = utils.find_all_entries_with_value_tsv(sample_data3, "cytosine")
    assert len(matches) == 1
    assert "cytosine" in matches[0]["Partial match"].lower()


def test_match_in_key(sample_data3):
    matches = utils.find_all_entries_with_value_tsv(sample_data3, "partial match")
    assert len(matches) == 3  # All have the key (even if value is empty)

def test_no_match_found(sample_data3):
    matches = utils.find_all_entries_with_value_tsv(sample_data3, "randomcompound")
    assert matches == []


#find_key_by_list_value
def sample_dict():
    return {
        "toy1.sbml": ["Adenine", "Guanine", "Cytosine"],
        "toy2.sbml": ["Thymine", "Uracil"],
        "toy3.sbml": ["Glucose", "Fructose"],
        "toy4.sbml": [],
        "toy5.sbml": ["ATP", "ADP", "AMP"],
    }



@pytest.fixture
def sample_dict():
    return {
        "toy1.sbml": ["Adenine", "Guanine", "Cytosine"],
        "toy2.sbml": ["Thymine", "Uracil"],
        "toy3.sbml": ["Glucose", "Fructose"],
        "toy4.sbml": [],
        "toy5.sbml": ["ATP", "ADP", "AMP"],
    }

def test_find_key_by_list_value_exact_match(sample_dict):
    key = utils.find_key_by_list_value(sample_dict, "Adenine")
    assert key == "toy1.sbml"

def test_find_key_by_list_value_case_insensitive(sample_dict):
    key = utils.find_key_by_list_value(sample_dict, "uracil")
    assert key == "toy2.sbml"

def test_find_key_by_list_value_value_not_found(sample_dict):
    key = utils.find_key_by_list_value(sample_dict, "XYZ")
    assert key is None



# check_formula_in_dict
def test_formula_found_exact_match():
    data = {'formula': ['H2O', 'CO2', 'C6H12O6']}
    assert utils.check_formula_in_dict(data, 'CO2') is True

def test_formula_found_case_insensitive():
    data = {'formula': ['h2o', 'co2', 'c6h12o6']}
    assert utils.check_formula_in_dict(data, 'CO2') is True

def test_formula_not_found():
    data = {'formula': ['H2O', 'CO2', 'C6H12O6']}
    assert utils.check_formula_in_dict(data, 'O2') is False

def test_formula_key_missing():
    data = {'other_key': ['H2O', 'CO2']}
    assert utils.check_formula_in_dict(data, 'H2O') is False

def test_formula_value_not_list_or_tuple():
    data = {'formula': 'H2O'}
    assert utils.check_formula_in_dict(data, 'H2O') is False

def test_formula_value_list_contains_non_string():
    data = {'formula': ['H2O', 42, None]}
    assert utils.check_formula_in_dict(data, 'H2O') is True
    assert utils.check_formula_in_dict(data, '42') is False  # because 42 is int, not str

def test_empty_formula_list():
    data = {'formula': []}
    assert utils.check_formula_in_dict(data, 'H2O') is False

def test_formula_value_is_none():
    data = {'formula': None}
    assert utils.check_formula_in_dict(data, 'H2O') is False



# ----------------------------
# Tests for process_unmatches if they are connnected to match metabolites
# ----------------------------

def test_no_conflict_all_unmatched_retained():
    df = pd.DataFrame({
        'A': ['Lactate', 'Pyruvate'],
        'B': ['Citrate', None]
    })
    match = ['Glucose']
    unmatch = ['Lactate', 'Pyruvate']
    
    result = utils.process_unmatches(df, match, unmatch)
    assert set(result) == {'Lactate', 'Pyruvate'}


def test_all_unmatched_match_with_others_ids_and_removed():
    df = pd.DataFrame({
        'A': ["['Glucose', 'Lactate']", 'WATER'],
        'B': ['Pyruvate', 'O2']
    })
    match = ['Glucose','WATER']
    unmatch = ['Lactate', 'Pyruvate','O2']
    
    result = utils.process_unmatches(df, match, unmatch)
    assert result == []  # All unmatched IDs are conflicted and removed


def test_partial_conflict_removal():
    df = pd.DataFrame({
        'A': ['Lactate', 'Glucose', 'Pyruvate'],
        'B': ['WATER', None, 'Citrate']
    })
    match = ['Glucose','WATER']
    unmatch = ['Lactate', 'Pyruvate', 'Citrate']
    
    result = utils.process_unmatches(df, match, unmatch)
    # Lactate appears with Glucose => removed
    # Pyruvate and Citrate are not in conflict => kept
    assert set(result) == {'Pyruvate', 'Citrate'}



def test_stringified_list_cells():
    df = pd.DataFrame({
        'A': ["['Glucose', 'ATP']", "['Lactate']"],
        'B': ["['Pyruvate']", None]
    })
    match = ['Glucose']
    unmatch = ['ATP', 'Lactate', 'Pyruvate']
    
    result = utils.process_unmatches(df, match, unmatch)
    # ATP and Pyruvate are in same row as Glucose → removed
    # Lactate is not → kept
    assert result == ['Lactate']



### Unmatch filtering

# Tests for normalize_cell
@pytest.mark.parametrize("input_val,expected", [
    ("['Glucose', 'Lactate']", ['glucose', 'lactate']),
    ("Glucose", ['glucose']),
    (["Pyruvate", "ATP"], ['pyruvate', 'atp']),
    (float('nan'), []),
])
def test_normalize_cell_metabolites(input_val, expected):
    output = utils.normalize_cell(input_val)
    assert isinstance(output, list)
    assert output == expected

# -------------------------------
# Tests for process_unmatches with metabolites
# -------------------------------

def test_metabolite_unmatch_conflict():
    df = pd.DataFrame({
        'A': ["['Glucose', 'Lactate']", "['Citrate']"],
        'B': ['Pyruvate', "['Glucose']"]
    })
    match_list = ['Glucose']
    unmatch_list = ['Lactate', 'Citrate', 'Pyruvate']
    
    result = utils.process_unmatches(df, match_list, unmatch_list)
    
    # 'Lactate' and 'Pyruvate' appear with 'Glucose' -> removed
    # 'Citrate' appears on a row with 'Glucose' (row 1) -> also removed
    assert result == []

def test_metabolite_unmatch_kept():
    df = pd.DataFrame({
        'A': ["['Lactate']", "['Pyruvate']"],
        'B': ["['Citrate']", None]
    })
    match_list = ['Glucose']
    unmatch_list = ['Lactate', 'Citrate', 'Pyruvate']
    
    result = utils.process_unmatches(df, match_list, unmatch_list)

    # No metabolite is on same line as 'Glucose' => all unmatch remain
    assert set(result) == {'Lactate', 'Citrate', 'Pyruvate'}

def test_metabolite_unmatch_partial_removal():
    df = pd.DataFrame({
        'A': ["['Lactate']", "['Glucose']", "['Pyruvate']"],
        'B': ["['Glucose']", None, "['Citrate']"]
    })
    match_list = ['Glucose']
    unmatch_list = ['Lactate', 'Pyruvate', 'Citrate']
    
    result = utils.process_unmatches(df, match_list, unmatch_list)

    # 'Lactate' is on same line as 'Glucose' → removed
    # 'Pyruvate' and 'Citrate' are not → kept
    assert set(result) == {'Pyruvate', 'Citrate'}



#Group of function for the smart merge

def test_split_and_clean_basic():
    assert utils.split_and_clean("A _AND_ B _AND_ C") == {"A", "B", "C"}
    assert utils.split_and_clean("  X _AND_ Y ") == {"X", "Y"}
    assert utils.split_and_clean("") == set()
    assert utils.split_and_clean(None) == set()

def test_build_similarity_graph_simple():
    dicts = [
        {'Metabolites': 'A _AND_ B', 'Match in database': 'YES'},
        {'Metabolites': 'B _AND_ C', 'Match in database': 'NO'},
        {'Metabolites': 'X', 'Match in database': 'YES'},
    ]
    keys = ['Metabolites', 'Match in database']
    graph = utils.build_similarity_graph(dicts, keys)
    assert 0 in graph and 1 in graph[0]
    assert 1 in graph and 0 in graph[1]


def test_get_connected_components_basic():
    graph = {
        0: {1},
        1: {0},
        2: set(),
    }
    comps = utils.get_connected_components(graph, 3)
    # Should return two components: {0,1} and {2}
    assert {0,1} in comps
    assert {2} in comps
    assert len(comps) == 2

def test_merge_dict_group_combines_properly():
    group = [
        {'Metabolites': 'A _AND_ B', 'Match in database': 'YES', 'Partial match': 'X'},
        {'Metabolites': 'B _AND_ C', 'Match in database': 'NO', 'Partial match': 'Y'},
    ]
    merged = utils.merge_dict_group(group)
    assert set(merged['Metabolites'].split(' _AND_ ')) == {'A', 'B', 'C'}
    # 'Match in database' and 'Partial match' should combine their values
    assert 'YES' in merged['Match in database']
    assert 'NO' in merged['Match in database']
    assert 'X' in merged['Partial match']
    assert 'Y' in merged['Partial match']




def test_smart_merge_merges_similar_dicts():
    dicts = [
        {'Metabolites': 'A _AND_ B', 'Match in database': 'YES'},
        {'Metabolites': 'B _AND_ C', 'Match in database': 'YES'},
        {'Metabolites': 'X _AND_ Y', 'Match in database': 'NO'},
    ]

    merged_results = utils.smart_merge(dicts)

    # Find the merged dict containing 'A', 'B', 'C' metabolites
    merged_dict = next(d for d in merged_results if 'A' in d.get('Metabolites', '') or 'C' in d.get('Metabolites', ''))

    # Split the merged string into individual metabolites
    metabolites = [m.strip() for m in merged_dict['Metabolites'].split(' _AND_ ')]

    # Assert that expected metabolites are present
    assert 'A' in metabolites
    assert 'B' in metabolites
    assert 'C' in metabolites

    # Also check that 'X' and 'Y' are in a separate merged dict
    other_merged = next(d for d in merged_results if 'X' in d.get('Metabolites', '') or 'Y' in d.get('Metabolites', ''))
    other_metabolites = [m.strip() for m in other_merged['Metabolites'].split(' _AND_ ')]

    assert 'X' in other_metabolites
    assert 'Y' in other_metabolites

def test_smart_merge_no_overlap_returns_same():
    dicts = [
        {'Metabolites': 'A', 'Match in database': 'YES'},
        {'Metabolites': 'B', 'Match in database': 'NO'},
    ]
    merged = utils.smart_merge(dicts)
    assert merged == dicts
