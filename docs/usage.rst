=====
Usage
=====

To use MetaNetMap in a project::

    import metanetmap


Command-line usage
------------------

Based on the input listed in ::doc:`inp_out_mapping`, ``metanetmap`` can be run with two main modes:
1. **Database building mode**: to create a third-party conversion datatable from MetaCyc or MetaNetX data.
2. **Mapping mode**: to map metabolomic data against metabolic networks using the conversion datatable. The mapping mode can be run in two different ways: 
    - classic mode: one or multiple metabolomic data files against a single metabolic network. 
    - community mode: one or multiple metabolomic data files against multiple metabolic networks.

Additionally, the **Test mode** runs predefined tests using toy data included in the package.

.. note::
  Before running the different modes, you must first build your own **conversion datatable**, as described below in the section *Custom third party database*.


Custom third party database
---------------------------

Non-trivial mapping between metabolomic data and metabolic networks requires a comprehensive knowledge base that links various identifiers from both sources. This is achieved through a third-party conversion datatable that acts as a bridge between the two datasets. It can currently be built using two different knowledge bases:

1. **Using MetaCyc files** (not provided with this package). You need a license to use MetaCyc data; here we use the information stored in the ``compounds.dat`` (or ``compounds_version.dat``) file — in order to build this conversion datatable.
2. **Using MetaNetX reference files**, which can be downloaded from `MetaNetX Reference Data <https://www.metanetx.org/mnxdoc/mnxref.html>`_

You can also provide your **own custom conversion data table**, as long as it follows the required column naming convention.  
This ensures that the **mapping mode** runs correctly.

.. note::

   The list and description of the required column names are available in the
   :doc:`inp_out_build` section.
  

- **Running database building mode for MetaCyc**:

  .. code-block:: bash

    metanetmap     build_db
                  --db            metacyc
                  -f              file/path/to/compounds.dat
                  --compfiles     file/path/to/complementary_datatable.tsv # Optional
                  --out_db        file/path/to/output_conversion_datatable.tsv # Optional
                  -q              quiet_mode (True/False) # Optional: False by default


- **Running database building mode for MetaNetX**:
  
  .. code-block:: bash

    metanetmap     build_db   
                  --db            metanetx
                  -f              file/path/to/MetaNetX_chem_prop.tsv  file/path/to/MetaNetX_chem_xref.tsv # Optional
                  --compfiles     file/path/to/complementary_datatable.tsv # Optional
                  --out_db        file/path/to/output_conversion_datatable.tsv # Optional
                  -q              quiet_mode (True/False) # Optional: False by default


.. note::

   The parameters ``file/path/to/output_conversion_datatable.tsv`` and 
   ``file/path/to/complementary_datatable.tsv`` are optional.

   - If the output argument **--out_db** is not provided, the output file ``file/path/to/output_conversion_datatable.tsv`` will be created by default in the current working directory.
   - If the argument **--compfiles** is not provided, the step for completing the conversion datatable with the user's additional mapping data ``file/path/to/complementary_datatable.tsv`` will be skipped.

   For the ``metanetx`` option, the ``-f`` argument specifies the input files. 
   If not provided by the user, the default ``chem_prop`` and ``chem_xref`` files 
   will be downloaded automatically.

   The file ``file/path/to/complementary_datatable.tsv`` can also be a manually curated file 
   created by users to include specific or custom IDs. 
   See the :doc:`usage_advanced` for more details.

  Depending on the selected knowledge base (``metanetx`` or ``metacyc``), the output file name will include the database as a prefix.


For more details on input/output data and directory structure, see :doc:`inp_out_build`


Mapping mode
-------------

Once a conversion data table is built, you can run MetaNetMap in two different sub-modes with a partial match option :

- **Classic mode**:
The classic mode allows you to input a single metabolomic annotation profile (tabulated file, `.maf` or `.tsv`) or a directory containing multiple metabolomic annotation profiles, and a unique metabolic network (`.sbml` or `.xml`) to which metabolites will be mapped.

  .. code-block:: bash

    metanetmap     classic
                  -s path/to/metabolic_networks.sbml  # Single SBML file
                  -a path/to/metabolomic_data/  # Single file or directory 
                  -d path/to/conversion_datatable.tsv 
                  -o path/to/output/directory/ # Optional
                  -p partial_match(True/False) # Optional explanation below
                  -q quiet_mode (True/False) # Optional: False by default
                   

  
- **Community mode**:
The **"community"** mode allows you to input a directory containing multiple metabolomic annotation profiles (tabulated files, `.maf` or `.tsv`), as well as a directory containing multiple metabolic networks (`.sbml` or `.xml`).
It will map each metabolomic data file against each metabolic network file, resulting in a comprehensive mapping across all combinations. This mode is useful for large-scale analyses involving a microbial community where multiple organisms and their associated networks are considered in the metabolomic study.


  .. code-block:: bash

    metanetmap     community
                  -s path/to/metabolic_networks_directory/ # Directory containing multiple SBML files
                  -a path/to/metabolomic_data/ # Single file or directory 
                  -d path/to/conversion_datatable.tsv
                  -o path/to/output/directory/ # Optional
                  -p partial_match(True/False) # Optional, explanation below
                  -q quiet_mode (True/False) # Optional: False by default


For more details on input/output data and directory structure, see :doc:`inp_out_mapping`, for more details on advanced methods (partial match, ambiguities, ...), see :doc:`usage_advanced`. In particular, the **partial match** option aims at increasing the chances of finding a match for metabolites that were not mapped during the initial run. This step is optional, as it can be time-consuming depending on the number of unmatched entries. To rescue those unmatched entries, specific strategies are applied, such as searching via ChEBI, InChIKey, or enantiomer simplification.
