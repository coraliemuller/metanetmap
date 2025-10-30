Quickstart
==========

To test the tool with toys data:

Two modes are available for testing, with an option to enable or disable **partial match**.

The **Partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).


Classic mode
The classic mode allows you to input a single metabolomics data file (.maf) and a directory containing multiple metabolic networks (.sbml/.xml).

.. code-block:: bash

    metanetmap test

Classic mode with partial match activated
.. code-block:: bash

    metanetmap test --partial_match

Community mode
The "community" mode allows you to input a directory containing multiple metabolomics data files (.maf), as well as a directory containing multiple metabolic networks(.sbml/.xml).

.. code-block:: bash

    metanetmap test --community 


Community mode with partial match activated
.. code-block:: bash

    metanetmap test --community --partial_match

For more details on modes refer to (see :doc:`overview`)

.. note::
   Metacyc database information related to the ontology of metabolites and pathways is not included in test option.

.. warning::
   We assume that you arrive at this step having installed the tool first (see above), for instance in a Python virtual environment, or conda (mamba) environment.

