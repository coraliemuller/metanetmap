
Input and ouput Data
==========

**Note:** All input files are required to use tab characters as field delimiters.


Database building mode
----------------------

Input data
~~~~~~~~~~~

+-------------------------+------------------------------------------------------------------------------------+
| File/Directory          | Description                                                                        |
+=========================+====================================================================================+
| metacyc_compounds       | Text file provided by the MetaCyc database                                         |
+-------------------------+------------------------------------------------------------------------------------+
| chem_xref               | Tabular file from MetaNetX with ref to others db                                   |
+-------------------------+------------------------------------------------------------------------------------+
| chem_prop               | Tabular file from MetaNetX with properties                                         |                                                                          
+-------------------------+------------------------------------------------------------------------------------+
| datatable_complementary | Tabular file provided by the user (see details below)                              |
+-------------------------+------------------------------------------------------------------------------------+
| output                  | Output directory for db download and conversion datatable results and logs         |
+-------------------------+------------------------------------------------------------------------------------+

.. note::
The ``datatable_complementary`` is a tabular file provided by the user.  
It allows users to add their own custom identifiers in order to improve matching with their metabolomic data.

**Requirements and structure:**

- The **first column must be** a ``UNIQUE-ID`` that links to the MetaCyc/MetaNetX database.
- All **following columns are free** and may contain any identifiers or names. Their column names will be automatically included in the main conversion datatable.
- The file must be in tabular format (e.g., TSV), with headers.

**Important notes:**

- If you have a metabolite **without a matching ``UNIQUE-ID`` in MetaCyc/MetaNetX**, you may assign it a **custom or fictional ID** in the first column.
- This fictional ``UNIQUE-ID`` will still be included in the conversion table, and **will be used if a match is found based on the name or identifier you provided.**
- Be sure to keep track of any custom or fictional IDs you create, so you can filter or manage them later if needed.


Output data
~~~~~~~~~~~

+-------------------------+----------------------------------------------------------------------+
| File/Directory          | Description                                                          |
+=========================+======================================================================+
| datatable_conversion    | Tabulated file, first column is the UNIQUE-ID in MetaCyc/MetaNetX    |
+-------------------------+----------------------------------------------------------------------+
| logs                    | Directory provides more detailed information                         |
+-------------------------+----------------------------------------------------------------------+

.. note::

  The ``datatable_conversion`` file acts as a bridge between the metabolomic data and the metabolic networks.
  It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``datatable_complementary`` file.
  This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite, and match them between the input metabolomic data and the metabolic networks.
  By leveraging both the MetaCyc/MetaNetX database and user-provided knowledge, the ``datatable_conversion`` enables robust and flexible mapping across diverse data sources.

  The ``logs`` directory contains detailed information about the processing steps.  
  It is useful for debugging, auditing, and understanding how the tool performed the mapping and handled the input data.


Mapping modes
--------------

Input data
~~~~~~~~~~~

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
   ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC``, ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``,
   ``CAS``, ``INCHI-KEY``, ``SMILES``


Output data
~~~~~~~~~~~

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

.. include:: input_data_details.rst
