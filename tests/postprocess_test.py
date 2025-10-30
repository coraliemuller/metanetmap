#!/bin/python
## MISTIC Project INRIA
## Author Muller Coralie
## Date: 2025/08/20
## Update: 2025/08/23

"""
Description:
Test postprocess
"""
from os import path
import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import MagicMock
from cobra import Model, Metabolite



from metanetmap import mapping
from metanetmap import utils

# /!\ INFO: 

#------------------------------------#
#        DIRECTORIES AND FILES       #
#------------------------------------#
TEST_TOYS_DIR = Path(__file__).parent.parent
DATATABLE_CONVERSION = path.join(TEST_TOYS_DIR,'src/metanetmap/toys_tests_data/conversion_datatable_toys.tsv')

def test_setup_harmonisation_output_basic():
    # Input data
    dic_tsv_results = [
        {'Metabolites': 'glucose', 'UNIQUE-ID': "GLUCOSE"},
        {'Metabolites': 'fructose', 'UNIQUE-ID': "FRUCTOSE"}
    ]
    keys_starter = ['Metabolites', 'UNIQUE-ID']
    unmatch_metabolites_total = ['sucrose', 'maltose']
    keys = ['COMMON-NAME', 'SMILE']

    # Call the function
    updated_results, keys_reorder = mapping.setup_harmonisation_output(
        dic_tsv_results.copy(), keys_starter, unmatch_metabolites_total, keys
    )

    # Expected unmatched entries added with empty fields except 'Metabolites'
    expected_unmatched_entries = [
        {'Metabolites': 'sucrose', 'UNIQUE-ID': '', 'Match via COMMON-NAME': '','Match via SMILE': ''},
        {'Metabolites': 'maltose', 'UNIQUE-ID': '',  'Match via COMMON-NAME': '','Match via SMILE': ''}
    ]

    expected_comlpleted_entries = [
        {'Metabolites': 'glucose', 'UNIQUE-ID': "GLUCOSE",'Match via COMMON-NAME': '','Match via SMILE': ''},
        {'Metabolites': 'fructose', 'UNIQUE-ID': "FRUCTOSE",'Match via COMMON-NAME': '','Match via SMILE': ''},
        {'Metabolites': 'sucrose', 'UNIQUE-ID': '', 'Match via COMMON-NAME': '','Match via SMILE': ''},
        {'Metabolites': 'maltose', 'UNIQUE-ID': '',  'Match via COMMON-NAME': '','Match via SMILE': ''}
    ]

    # Check unmatched entries appended
    assert updated_results[-2:] == expected_unmatched_entries
    assert updated_results == expected_comlpleted_entries

    # Check all dictionaries have keys from keys_starter
    for entry in updated_results:
        for key in keys_starter:
            assert key in entry

    # Check 'Match via {key}' columns are added and initialized empty
    for entry in updated_results:
        for key_name in keys:
            match_key = f'Match via {key_name}'
            assert match_key in entry
            assert entry[match_key] == ""

    # Check keys_reorder has starter keys plus match keys
    expected_keys = keys_starter + [f'Match via {k}' for k in keys]
    assert set(expected_keys).issubset(set(keys_reorder))


# ----------------------------------
# Tests for normalize_cell_preserve_case
# ----------------------------------

@pytest.mark.parametrize("input_val,expected", [
    ("['Glucose', 'Lactate']", ['Glucose', 'Lactate']),
    ("Glucose", ['Glucose']),
    (["ATP", "NADH"], ['ATP', 'NADH']),
    (None, []),
    (float('nan'), []),
])
def test_normalize_cell_preserve_case(input_val, expected):
    assert utils.normalize_cell_preserve_case(input_val) == expected

# ----------------------------------
# Tests for extract_metabolite_combinations
# ----------------------------------


def test_extract_combinations_single_hit():
    df = pd.DataFrame({
        'A': ['Glucose'],
        'B': [None]
    })
    metabolites = ['glucose']
    
    result = utils.extract_metabolite_combinations(metabolites, df)
    
    assert result == ['Glucose']


def test_extract_combinations_none_found():
    df = pd.DataFrame({
        'A': ["['ATP']", "Creatine"],
        'B': ["['NAD+']", None]
    })
    metabolites = ['glucose', 'pyruvate']
    
    result = utils.extract_metabolite_combinations(metabolites, df)

    assert result == []

def test_extract_combinations_preserve_case():
    df = pd.DataFrame({
        'A': ["['gLuCose', 'LACTATE']"],
        'B': ["PYRUVATE"]
    })
    metabolites = ['glucose', 'lactate', 'pyruvate']
    
    result = utils.extract_metabolite_combinations(metabolites, df)
    
    assert result == ['gLuCose _AND_ LACTATE _AND_ PYRUVATE']
