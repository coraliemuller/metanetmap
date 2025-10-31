=====
Usage
=====

To use MetaNetMap in a project::

    import metanetmap


Command-line usage
------------------

Based on the input listed in :doc:`input_data`, ``metanetmap`` can be run in four mode:

.. note::
  Before running the different modes, you must first build your own **data table conversion**.

There are two main ways to do this:

1. **Using MetaCyc files** (not provided with this package). You need access and permission to use MetaCyc data — specifically the ``compounds.dat`` (or ``compounds_version.dat``) file — in order to build this datatable conversion.
2. **Using MetaNetX reference files**, which can be downloaded from:

   - `MetaNetX Reference Data <https://www.metanetx.org/mnxdoc/mnxref.html>`_

Custom Conversion Tables
------------------------

You can also provide your **own custom conversion data table**, as long as it follows the required column naming convention.  
This ensures that the **mapping mode** runs correctly.

.. note::

   The list and description of the required column names are available in the
   :doc:`input_data` section.
  

- **Run database building mode for Metacyc**:

  .. code-block:: bash

    metanetmap     build_db   \
                  --db            metacyc\
                  -f              metacyc_compounds_dat/file/path 
                  --compfiles     datatable_complementary_tsv/file/path
                  --out_db        output_conversion_datatable_tsv/file/path 
                  -q              quiet_mode (True/False) # Optional


- **Run database building mode for MetaNetX**:
  
  .. code-block:: bash

    metanetmap     build_db   \
                  --db            metanetx\
                  -f              MetaNetX_chem_prop/file/path  MetaNetX_chem_xref/file/path
                  --compfiles     datatable_complementary_tsv/file/path
                  --out_db        output_conversion_datatable_tsv/file/path 
                  -q              quiet_mode (True/False) # Optional


.. note::

   The parameters ``output_conversion_datatable_tsv/file/path`` and 
   ``datatable_complementary_tsv/file/path`` are optional.

   - If ``output_conversion_datatable_tsv/file/path`` is empty, the file will be downloaded 
     to the root directory.
   - If ``datatable_complementary_tsv/file/path`` is empty, the complementary step will 
     be ignored.

   For the ``metanetx`` option, the ``-f`` argument specifies the input files. 
   If not provided by the user, the default ``chem_prop`` and ``chem_xref`` files 
   will be downloaded automatically.

   The file ``datatable_complementary_tsv/file/path`` may also be a manually curated file 
   created by users to include specific or custom IDs. 
   See the documentation for more details.

  Depending on the selected mode (``metanetx`` or ``metacyc``), the output file name will include the mode as a prefix.


After this you can run MetaNetMap in two different modes with a partial match option :


- **Classic mode**:
The classic mode allows you to input a single metabolomics data file and a directory containing multiple metabolic networks.

  .. code-block:: bash

    metanetmap     classic
                  -s metabolic_networks_dir/directory/path \
                  -a metabolomics_data/file/path \
                  -d datatable_conversion_tsv/file/path \
                  -o save/path \  # Optional
                  -p partial_match(True/False) \  # Optional explanation below
                  -q quiet_mode (True/False) # Optional
                   

  
- **Community mode**:
The "community" mode allows you to input a directory containing multiple metabolomics data files, as well as a directory containing multiple metabolic networks.

  .. code-block:: bash

    metanetmap     community
                  -s metabolic_networks_dir/directory/path \
                  -a metabolomics_data/directory/path \
                  -d datatable_conversion_tsv/file/path \
                  -o save/path \  # Optional
                  -p partial_match(True/False) \  # Optional, explanation below
                  -q quiet_mode (True/False) # Optional



- **Partial match**:
The **partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).

After this processing step, the entire mapping pipeline is re-executed, taking the modifications into account.

**The following treatments are applied:**

- **CHEBI** *(only if a CHEBI column exists in the metabolomics data)*:  
  For each row containing a CHEBI ID, the API from EBI is used to retrieve the full CHEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **INCHIKEY**:  
  An INCHIKEY is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract only this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomics data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomics datasets.



For more details on input/output data and directory structure, see below.

Input Data
==========

**Note:** All input files, including CSV and TSV formats, are required to use tab characters as field delimiters.


Summary of input files for database building mode
----------------------

+-------------------------+-------------------------------------------------------+
| File/Directory          | Description                                           |
+=========================+=======================================================+
| metacyc_compounds       | Text file provided by the MetaCyc database            |
+-------------------------+-------------------------------------------------------+
| chem_xref               | Tabular file from MetaNetX with ref to others db      |
+-------------------------+-------------------------------------------------------+
| chem_prop               | Tabular file from MetaNetX with properties            |                                                                          
+-------------------------+-------------------------------------------------------+
| datatable_complementary | Tabular file provided by the user (see details below) |
+-------------------------+-------------------------------------------------------+
| output -o               | Output directory for mapping results and logs         |
+-------------------------+-------------------------------------------------------+

.. note::
The ``datatable_complementary`` is a tabular file provided by the user.  
It allows users to add their own custom identifiers in order to improve matching with their metabolomics data.

**Requirements and structure:**

- The **first column must be** a ``UNIQUE-ID`` that links to the MetaCyc/MetaNetX database.
- All **following columns are free** and may contain any identifiers or names. Their column names will be automatically included in the main conversion datatable.
- The file must be in tabular format (e.g., TSV or CSV), with headers.

**Important notes:**

- If you have a metabolite **without a matching ``UNIQUE-ID`` in MetaCyc/MetaNetX**, you may assign a **custom or fictional ID** in the first column.
- This fictional ``UNIQUE-ID`` will still be included in the conversion table, and **will be used if a match is found based on the name or identifier you provided.**
- Be sure to keep track of any custom or fictional IDs you create, so you can filter or manage them later if needed.


Summary of input files for mapping modes
----------------------

+---------------------+----------------------------------------------------------------------+
| File/Directory      | Description                                                          |
+=====================+======================================================================+
| MetaNetMap output   | Output directory for mapping results and logs                        |
+---------------------+----------------------------------------------------------------------+
| metabolic_networks  | Path to the directory with .sbml or/and .xml files                   |
+---------------------+----------------------------------------------------------------------+
| metabolomics_data   | Tabulated file, (cf note below for details)                          |
+---------------------+----------------------------------------------------------------------+
| datatable_conversion| Tabulated file, first column is the UNIQUE-ID in MetaCyc/MetaNetX    |
+---------------------+----------------------------------------------------------------------+


.. note::
  For **metabolomics_data**:
  Column names must follow a specific naming convention. 
  Metabolomics data files must include column names that follow a specific naming convention in order to be properly processed by the tool during the mapping step.
 
  The following column names are recognized:

   ``UNIQUE-ID``, ``CHEBI``, ``COMMON-NAME``, ``ABBREV-NAME``, ``SYNONYMS``,
   ``ADD-COMPLEMENT``, ``MOLECULAR-WEIGHT``, ``MONOISOTOPIC-MW``, ``SEED``,
   ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC`` , ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``,
   ``CAS``, ``INCHI-KEY``, ``SMILES``



Output Data
==========

Summary of output file for database building mode
----------------------
+-------------------------+----------------------------------------------------------------------+
| File/Directory          | Description                                                          |
+=========================+======================================================================+
| datatable_conversion    | Tabulated file, first column is the UNIQUE-ID in MetaCyc/MetaNetX    |
+-------------------------+----------------------------------------------------------------------+
| logs                    | Directory provides more detailed information                         |
+-------------------------+----------------------------------------------------------------------+

.. note::

  The ``datatable_conversion`` file acts as a bridge between the metabolomics data and the metabolic networks.
  It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``datatable_complementary`` file.
  This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.
  By leveraging both the MetaCyc/MetaNetX database and user-provided enhancements, the ``datatable_conversion`` enables robust and flexible mapping across diverse data sources.

  The ``logs`` directory contains detailed information about the processing steps.  
  It is useful for debugging, auditing, and understanding how the tool performed the mapping and handled the input data.

  A conversion data table has already been built and is provided from MetaNetX in ``data/metanetx_conversion_datatable.tsv``.


Summary of output file for mapping modes
----------------------
+-------------------------+-------------------------------------------------------------+
| File/Directory          | Description                                                 |
+=========================+=============================================================+
| mapping_results         | Tabulated file with match/unmatch results                   |
+-------------------------+-------------------------------------------------------------+
| logs                    | Directory provides more detailed information                |
+-------------------------+-------------------------------------------------------------+


.. note::

**Output file format**

The name of the output file depends on the processing mode:

- In **community mode**, the file is named as: ``community_mapping_results_YYYY-MM-DD_HH:MM:SS.tsv``
- In **classic mode**, the file is named as: ``mapping_results_YYYY-MM-DD_HH:MM:SS.tsv``
- If **partial match** is activated, the filename will include ``partial_match`` to indicate this.

**File content and column structure**

The output is a tabular file containing several columns with mapping results and metadata:

1. **Metabolite Matches**  
   Lists the metabolite names that matched.  
   If multiple matches are found for a single input (i.e., duplicates), they are joined using ``_AND_``.  

2. **MetaCyc/MetaNetX UNIQUE-ID Match (from `datatable_conversion`)**  
   Indicates whether a match was found through the MetaCyc/MetaNetX conversion table using a ``UNIQUE-ID``.  
   If two UNIQUE-IDs match the same input, they are separated by ``_AND_`` and flagged as uncertain.  
   These entries are also reflected in the **partial** column due to ambiguity.

3. **Input File Match (metabolomics data)**  
   In **classic mode**, this column shows the identifier from the input file that matched with the SBML model.  
   In **community mode**, this column contains a list (e.g., ``[data1, data4]``) indicating the specific files in which matches were found.  
   Additional details about the exact identifiers used in the networks can be found in the logs.

4. **Partial Match**  
   This column contains any uncertain or ambiguous matches:
   
   - Duplicates (same metabolite matched multiple entries)
   - Matches resulting from post-processing (enabled when partial matching is active), such as:
     - CHEBI ontology expansion
     - INCHIKEY simplification
     - Enantiomer removal

   These matches require manual review and are also logged in detail.

5. **Other Columns**  
   The remaining columns correspond to identifiers or metadata from the metabolomics data.  
   Each cell contains ``YES`` to indicate that a match was found on the ID of that column in the metabolomics data.
