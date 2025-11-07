=====
Usage
=====

To use MetaNetMap in a project::

    import metanetmap


Command-line usage
------------------

Based on the input listed in ::doc:`inp_out_mapping`, ``metanetmap`` can be run in four mode

.. note::
  Before running the different modes, you must first build your own **data table conversion**.

There are two main ways to do this:

1. **Using MetaCyc files** (not provided with this package). You need access and permission to use MetaCyc data — specifically the ``compounds.dat`` (or ``compounds_version.dat``) file — in order to build this datatable conversion.
2. **Using MetaNetX reference files**, which can be downloaded from:

   - `MetaNetX Reference Data <https://www.metanetx.org/mnxdoc/mnxref.html>`_

Custom third party database
------------------------

You can also provide your **own custom conversion data table**, as long as it follows the required column naming convention.  
This ensures that the **mapping mode** runs correctly.

.. note::

   The list and description of the required column names are available in the
   :doc:`inp_out_build` section.
  

- **Run database building mode for MetaCyc**:

  .. code-block:: bash

    metanetmap     build_db   \
                  --db            metacyc\
                  -f              metacyc_compounds_dat/file/path 
                  --compfiles     datatable_complementary_tsv/file/path # Optional
                  --out_db        output_conversion_datatable_tsv/file/path # Optional
                  -q              quiet_mode (True/False) # Optional: False by default


- **Run database building mode for MetaNetX**:
  
  .. code-block:: bash

    metanetmap     build_db   \
                  --db            metanetx\
                  -f              MetaNetX_chem_prop/file/path  MetaNetX_chem_xref/file/path # Optional
                  --compfiles     datatable_complementary_tsv/file/path # Optional
                  --out_db        output_conversion_datatable_tsv/file/path # Optional
                  -q              quiet_mode (True/False) # Optional: False by default


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


For more details on input/output data and directory structure, see :doc:`inp_out_build`


Run mapping mode
------------------------

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
                  -q quiet_mode (True/False) # Optional: False by default
                   

  
- **Community mode**:
The "community" mode allows you to input a directory containing multiple metabolomics data files, as well as a directory containing multiple metabolic networks.

  .. code-block:: bash

    metanetmap     community
                  -s metabolic_networks_dir/directory/path \
                  -a metabolomics_data/directory/path \
                  -d datatable_conversion_tsv/file/path \
                  -o save/path \  # Optional
                  -p partial_match(True/False) \  # Optional, explanation below
                  -q quiet_mode (True/False) # Optional: False by default


For more details on input/output data and directory structure, see :doc:`inp_out_mapping`, for more details on advanced methods (partial match, ambiguities, ...), see :doc:`usage_advanced`

