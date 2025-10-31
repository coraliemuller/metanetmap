#!/bin/python
## MISTIC Project INRIA/INRAE
## Author Muller Coralie
## Date: 2025/08/19
## Update: 2025/10/31

"""
Description:
Test methods for partial
"""

import pytest
from os import path
from unittest.mock import MagicMock
from unittest.mock import AsyncMock, patch

from metanetmap import mapping
from metanetmap import utils


#-----------------------#
#      enantiomers      #
#-----------------------#


def test_remove_enantiomer_and_inchey_metadata():
    input_metadata = {
        "glucose": {
            "ID": ["D-glucose", "glucose", "alpha-D-glucose"],
            "biocyc": ["D-glucose", "beta-L-glucose"]
        },
        "fructose": {
            "ID": ["L-fructose", "fructose"],
            "biocyc": []
        }
    }

    expected_output = {
        "glucose": {
            "ID": ["glucose", "glucose", "glucose"],
            "biocyc": ["glucose", "glucose"]
        },
        "fructose": {
            "ID": ["fructose", "fructose"],
            "biocyc": []
        }
    }

    result = mapping.remove_enantiomer_and_Inchey_metadata(input_metadata)
    assert result == expected_output


#----------------------------------------------------#
#             Chebi unmatch test                     #
#----------------------------------------------------#



# Fetch CHEBI step

@pytest.mark.asyncio
async def test_fetch_chebi_entity_success():
    """Test that fetch_chebi_entity returns the correct JSON data on success."""
    fake_json = {
        "id": 36023,
        "chebi_accession": "CHEBI:36023",
        "name": "vaccenic acid",
        "stars": 3,
        "definition": (
            "An octadecenoic acid having a double bond at position 11; "
            "and which can occur in <i>cis</i>- or <i>trans</i>- configurations."
        ),
        "ascii_name": "vaccenic acid"
    }

    # Mock réponse HTTP
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=fake_json)

    # Mock du contexte async with
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = False

    # Mock de session
    session = MagicMock()
    session.get.return_value = mock_context

    # Appel de la fonction à tester
    result = await utils.fetch_chebi_entity(session, "CHEBI:36023")

    print("\n--- RESULT ---")
    print(result)
    print("--------------\n")

    # Vérifications
    assert isinstance(result, dict)
    assert result["id"] == 36023
    assert result["chebi_accession"] == "CHEBI:36023"
    assert result["ascii_name"] == "vaccenic acid"




@pytest.mark.asyncio
async def test_fetch_chebi_entity_failure_status():
    """Test fetch_chebi_entity returns None for non-200 status."""

    # Create a mock response that works with 'async with'
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.json = AsyncMock(return_value={})

    # Make it act as an async context manager
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = None

    # Patch session.get to return the mock_response directly (not as coroutine)
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    # Call the async function with the mocked session
    result = await utils.fetch_chebi_entity(mock_session, "1234")

    assert result is None



def test_get_chebi_links_missing_relations():
    """Test when outgoing/incoming lists are empty."""
    fake_json = {
        "ontology_relations": {
            "outgoing_relations": [],
            "incoming_relations": [],
        }
    }

    result = utils.get_chebi_links(fake_json)
    assert result == {"outgoings": [], "incomings": []}


def test_get_chebi_links_no_is_a_relations():
    """Test when there are relations but none with type 'is a'."""
    fake_json = {
        "ontology_relations": {
            "outgoing_relations": [
                {"final_id": "100", "final_name": "foo", "relation_type": "part of"}
            ],
            "incoming_relations": [
                {"init_id": "200", "final_name": "bar", "relation_type": "related to"}
            ],
        }
    }

    result = utils.get_chebi_links(fake_json)
    # Should return empty lists because no "is a" relationships
    assert result == {"outgoings": [], "incomings": []}


# chebi_parents_childrens
def test_chebi_parents_childrens_with_names():
    """Test that parent and child relations with names are added correctly."""
    list_unmatch_to_reload = {"water": ["CHEBI:15377"]}
    list_relation_chebi = {
        "outgoings": [{"chebi_id": "15378", "name": "hydroxide ion"}],
        "incomings": [{"chebi_id": "15379", "name": "hydron"}],
    }

    result = utils.chebi_parents_childrens(list_unmatch_to_reload, list_relation_chebi, "water")

    expected = {
        "water": [
            "CHEBI:15377",
            "CHEBI:15378", "hydroxide ion",
            "CHEBI:15379", "hydron",
        ]
    }

    assert result == expected


def test_chebi_parents_childrens_without_name():
    """Test behavior when some related entities do not have a name."""
    list_unmatch_to_reload = {"acetate": ["CHEBI:30089"]}
    list_relation_chebi = {
        "outgoings": [{"chebi_id": "15377", "name": None}],
        "incomings": [{"chebi_id": "12345"}],
    }

    result = utils.chebi_parents_childrens(list_unmatch_to_reload, list_relation_chebi, "acetate")

    expected = {
        "acetate": [
            "CHEBI:30089",
            "CHEBI:15377",
            "CHEBI:12345",
        ]
    }

    assert result == expected


def test_chebi_parents_childrens_empty_relations():
    """Test that the function handles empty relation lists."""
    list_unmatch_to_reload = {"hydron": ["CHEBI:15379"]}
    list_relation_chebi = {"outgoings": [], "incomings": []}

    result = utils.chebi_parents_childrens(list_unmatch_to_reload, list_relation_chebi, "hydron")

    # The structure should remain unchanged
    assert result == {"hydron": ["CHEBI:15379"]}


def test_chebi_parents_childrens_multiple_entries():
    """Test handling of multiple parents and children."""
    list_unmatch_to_reload = {"ammonia": ["CHEBI:16134"]}
    list_relation_chebi = {
        "outgoings": [
            {"chebi_id": "15377", "name": "water"},
            {"chebi_id": "17014", "name": "base"},
        ],
        "incomings": [
            {"chebi_id": "12345", "name": "protonated ammonia"},
            {"chebi_id": "54321", "name": "ammonium"},
        ],
    }

    result = utils.chebi_parents_childrens(list_unmatch_to_reload, list_relation_chebi, "ammonia")

    assert "CHEBI:15377" in result["ammonia"]
    assert "base" in result["ammonia"]
    assert "ammonium" in result["ammonia"]
    assert result["ammonia"][0] == "CHEBI:16134"


