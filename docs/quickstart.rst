Quickstart
==========

.. warning::
   We assume that you arrive at this step having installed the tool first (see :doc:`installation`), for instance in a Python virtual environment, or conda (mamba) environment.

The following quickstart guide will help you get started with MetaNetMap. Code examples are provided for each step, applying to toy data included in the repository.

Two modes are available for testing, with an option to enable or disable **partial match**.

The **Partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).

Tests use a dedicated third-party conversion table relying on MetaCyc data. A conversion data table can be created easily using the folowing command: 

.. code-block:: bash

    metanetmap build_db --db metanetx 

Classic mode
------------

The classic mode allows you to input a single metabolomics data file (`.maf` or `.tsv`) or a directory containing multiple metabolomics data files, and a unique metabolic network (`.sbml` or `.xml`).

.. code-block:: bash

    metanetmap test

Classic mode with partial match activated

.. code-block:: bash

    metanetmap test --partial_match

Community mode
----------------
The **"community"** mode allows you to input a directory containing multiple metabolomics data files (`.maf` or `.tsv`), as well as a directory containing multiple metabolic networks (`.sbml` or `.xml`).

.. code-block:: bash

    metanetmap test --community 


Community mode with partial match activated

.. code-block:: bash

    metanetmap test --community --partial_match

For more details on modes refer to :doc:`usage`.

.. note::
   Complete MetaCyc database information related to the ontology of metabolites and pathways is not included in test option because of licensing restrictions.
