
Inputs and outputs: Third-party database building mode
==========

.. note:: 
  All input files are required to use tab characters as field delimiters.

Structure
------------------

 Example of directory structure (but files and directories can be placed anywhere):

  .. code-block:: text

    example:
    MetaCyc_db
    ├── metacyc_compounds.dat (MetaCyc)
    MetaNetX_db
    ├── chem_xref.tsv (MetaNetX)
    ├── chem_prop.tsv (MetaNetX)
    Complementary
    ├── complementary_datatable.tsv (for MetaCyc/MetaNetX)
    logs/



Input data
-----------

.. note::
  Not all data listed below are mandatory. 
  The easiest way to build a third-party database is to use only MetaNetX data (``chem_xref.tsv`` and ``chem_prop.tsv`` files). 
  
  You can provide the files or directly let the tool download them for you with the command ``metanetmap build_db --db metanetx``.


+-------------------------+------------------------------------------------------------------------------------+
| File/Directory          | Description                                                                        |
+=========================+====================================================================================+
| metacyc_compounds       | Text file provided by the MetaCyc database                                         |
+-------------------------+------------------------------------------------------------------------------------+
| chem_xref               | Tabular file from MetaNetX with ref to others db                                   |
+-------------------------+------------------------------------------------------------------------------------+
| chem_prop               | Tabular file from MetaNetX with properties                                         |                                                                          
+-------------------------+------------------------------------------------------------------------------------+
| complementary_datatable | Tabular file provided by the user (see details below)                              |
+-------------------------+------------------------------------------------------------------------------------+
| output                  | Output directory for db download and conversion datatable results and logs         |
+-------------------------+------------------------------------------------------------------------------------+


Details input files 
~~~~~~~~~~~

.. toggle:: MetaCyc Compounds

   metacyc_compounds (MetaCyc):
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^

     ``compounds.dat`` has to be provided by the user. Access to this file requires a licence for MetaCyc

   The following is a raw entry for the compound **WATER** from a MetaCyc flat file `.dat` extension. 
   The file is structured as key-value pairs, where each line represents a specific property or annotation of the compound.

   Some keys, such as `CHEMICAL-FORMULA`, `SYNONYMS`, or `DBLINKS`, may occur multiple times. Values can contain nested content, quotes, or formatting (e.g. HTML tags in names).

   *Some Key Characteristics (non-exhaustive)*
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | **Field**                | **Description**                                                                                       |
   +==========================+=======================================================================================================+
   | ``UNIQUE-ID``            | Primary identifier of the compound in the MetaCyc database.                                           |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``TYPES``                | Declares the type of entity — typically ``Compound``, but can also be other biological entities.      |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``COMMON-NAME``          | Human-readable compound name. May contain HTML formatting.                                            |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``CHEMICAL-FORMULA``     | Chemical composition split across multiple lines, each specifying an element and its count.           |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``DBLINKS``              | Cross-references to external databases such as BiGG, ChEBI, HMDB, KEGG, PubChem, etc. Multiple lines. |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``INCHI``                | Standard InChI string describing the molecular structure.                                             |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``INCHI-KEY``            | Hashed InChI identifier (short, fixed-length string) used for quick comparison of chemical structures.|
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   |``INSTANCE-NAME-TEMPLATE``| A template indicating how this compound ID is generated or structured (e.g., starts with ``CPD-``).   |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``LOGP``                 | Octanol–water partition coefficient (logP), representing hydrophobicity.                              |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``MOLECULAR-WEIGHT``     | Average molecular weight based on atomic composition.                                                 |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``MONOISOTOPIC-MW``      | Exact mass using the most abundant isotope for each element.                                          |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``NON-STANDARD-INCHI``   | Alternative or non-standard InChI representation.                                                     |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``POLAR-SURFACE-AREA``   | Topological polar surface area (TPSA) of the molecule.                                                |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``SMILES``               | Simplified Molecular Input Line Entry System (SMILES) string representing the structure.              |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
   | ``SYNONYMS``             | Alternate or common names for the compound. Can appear on multiple lines.                             |
   +--------------------------+-------------------------------------------------------------------------------------------------------+
 
   
   *Example Compound Entry in the MetaCyc file*
   ::
       UNIQUE-ID - Primary identifier within the MetaCyc database (WATER).
       TYPES - Declares the entity as a Compound.
       COMMON-NAME - H<sub>2</sub>O.
       CHEMICAL-FORMULA - Stored in multiple lines for atomic composition.
       CHEMICAL-FORMULA - Stored in multiple lines for atomic composition.
       DBLINKS - Cross-references to external databases such as BIGG, HMDB, ChEBI, etc.
       DBLINKS - (CHEBI "15377" NIL |taltman| 3452438148 NIL NIL)
       DBLINKS - (LIGAND-CPD "C00001" NIL |kr| 3346617699 NIL NIL)
       INCHI - InChI=1S/H2O/h1H2 Chemical structure descriptors.
       INCHI-KEY - InChIKey=XLYOFNOQVPJJNP-UHFFFAOYSA-N
       INSTANCE-NAME-TEMPLATE - CPD-*
       LOGP - -0.5
       MOLECULAR-WEIGHT - 18.015
       MONOISOTOPIC-MW - 18.0105646863
       NON-STANDARD-INCHI - InChI=1S/H2O/h1H2
       POLAR-SURFACE-AREA - 1.
       SMILES - O
       SYNONYMS - Alternate names for the compound.
       SYNONYMS - H2O
       SYNONYMS - hydrogen oxide
       SYNONYMS - water
   
   
   - **chem_xref.tsv (MetaNetX)**:
     Tabular file provided by the user from MetaNetX website. It can also be directly downloaded by MetaNetMap using the command:
     
     .. code-block:: bash
   
         metanetmap build_db --db metanetx
   
   Each line represents an entry linking different identifiers or names for the same metabolite.
   This kind of table is commonly used as a mapping table between databases such as MetaNetX, SEED, BiGG, or ChEBI.
   
   
   +-------------+---------------+----------------------------------------------------------+
   | **Column**  | **Name**      | **Description**                                          |
   +=============+===============+==========================================================+
   | 1           | source        | Source database and identifier (e.g. mnx:BIOMASS,        |
   |             |               | seedM:cpd11416, CHEBI:16234...)                          |
   +-------------+---------------+----------------------------------------------------------+
   | 2           | ID            | Corresponding MetaNetX or normalized identifier (e.g.    |
   |             |               | MNXM01, MNXM02, BIOMASS)                                 |
   +-------------+---------------+----------------------------------------------------------+
   | 3           | description   | Descriptive information, including names, synonyms, or   |
   |             |               | notes separated by ``||``                                |
   +-------------+---------------+----------------------------------------------------------+
   
   - *Example Entries*
   .. code-block:: text
      Source          ID          Description
      BIOMASS         BIOMASS     BIOMASS
      mnx:BIOMASS     BIOMASS     BIOMASS
      seedM:cpd11416  BIOMASS     Biomass
      MNXM01          MNXM01      PMF||Translocated proton that accounts for the Proton Motive Force
      CHEBI:16234     MNXM02      hydroxide||HO-||Hydroxide ion||OH(-)||hydridooxygenate(1-)

   
   .. note::
     - The ``||`` separator indicates multiple synonyms or alternative names.
     - Identifiers such as ``MNXM##`` correspond to MetaNetX universal metabolite IDs.
     - Lines describing ``BIOMASS`` or ``PMF`` represent pseudo-metabolites used in
     metabolic network models.
   
   
   
   - **chem_prop.tsv (MetaNetX):**
   
   This table lists basic information for metabolites or pseudo-metabolites,
   including chemical formulas, charges, molecular masses, and structure encodings.
   It links each metabolite to a reference identifier from a source database.
   
   This file does not have to be provided by the user if MetaNetMap is used to download the necessary data, with the command:
     
     .. code-block:: bash
   
         metanetmap build_db --db metanetx
   
   
   - Table Structure\
   +-------------+----------------+----------------------------------------------------------+
   | **Column**  | **Name**       | **Description**                                          |
   +=============+================+==========================================================+
   | 1           | ID             | Unique internal or MetaNetX identifier (e.g. MNXM01)     |
   +-------------+----------------+----------------------------------------------------------+
   | 2           | name           | Common metabolite name (e.g. PMF, OH(-), H3O(+))         |
   +-------------+----------------+----------------------------------------------------------+
   | 3           | reference      | Source or cross-reference identifier (e.g. mnx:PMF)      |
   +-------------+----------------+----------------------------------------------------------+
   | 4           | formula        | Molecular formula (e.g. H, HO, H3O)                      |
   +-------------+----------------+----------------------------------------------------------+
   | 5           | charge         | Net electrical charge (integer, may be 0, -1, +1, etc.)  |
   +-------------+----------------+----------------------------------------------------------+
   | 6           | mass           | Molecular mass in Daltons (Da)                           |
   +-------------+----------------+----------------------------------------------------------+
   | 7           | InChI          | IUPAC International Chemical Identifier string           |
   +-------------+----------------+----------------------------------------------------------+
   | 8           | InChIKey       | Hashed representation of the InChI                       |
   +-------------+----------------+----------------------------------------------------------+
   | 9           | SMILES         | Simplified molecular structure in SMILES format          |
   +-------------+----------------+----------------------------------------------------------+
   
   - *Example Entries*\
   .. code-block:: text
   
      BIOMASS BIOMASS mnx:BIOMASS
      MNXM01  PMF     mnx:PMF H       1       1.00794 InChI=1S/p+1    GPRLSGONYQIRFK-UHFFFAOYSA-N     [H+]
      MNXM02  OH(-)   mnx:HYDROXYDE   HO      -1      17.00700        InChI=1S/H2O/h1H2/p-1   XLYOFNOQVPJJNP-UHFFFAOYSA-M     [H][O-]
      MNXM03  H3O(+)  mnx:OXONIUM     H3O     1       19.02300        InChI=1S/H2O/h1H2/p+1   XLYOFNOQVPJJNP-UHFFFAOYSA-O     [H][O+]([H])[H]
   
   
   
   .. note::
     - Some entries (like ``BIOMASS`` or ``PMF``) represent pseudo-metabolites used
     in constraint-based metabolic models.
     - ``InChI`` and ``SMILES`` are standard line notations for representing chemical
     structures computationally.
     - Charges and masses are provided for use in biochemical simulations and model
     balancing.
   
   
   
   - **complementary_datatable**:  
     Tabular file provided by the user
   
   (MetaCyc)\
   +-----------------+---------------------------------------+----------+----------+
   | **UNIQUE-ID**   | **ADD-COMPLEMENT**                    | **BIGG** | **SEED** |
   +=================+=======================================+==========+==========+
   | ``CPD-7100``    | (2S)-2-isopropyl-3-oxosuccinic acid   |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``DI-H-OROTATE``| (S)-dihydroorotic acid                |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``SHIKIMATE-5P``| 3-phosphoshikimic acid                |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``DIAMINONONANOATE`` | 7,8-diaminononanoate             | dann     |          |
   +-----------------+---------------------------------------+----------+----------+
   
   
   (MetaNetX)\
   +-----------------+---------------------------------------+----------+----------+
   | **UNIQUE-ID**   | **ADD-COMPLEMENT**                    | **BIGG** | **SEED** |
   +=================+=======================================+==========+==========+
   | ``MNXM1602``    | (2S)-2-isopropyl-3-oxosuccinic acid   |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``MNXM252``     | (S)-dihydroorotic acid                |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``MNXM1265``    | 3-phosphoshikimic acid                |          |          |
   +-----------------+---------------------------------------+----------+----------+
   | ``MNXM1140``    | 7,8-diaminononanoate                  | dann     |          |
   +-----------------+---------------------------------------+----------+----------+

   
   The ``complementary_datatable`` is a tabular file provided by the user.  
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
-----------

+-------------------------+----------------------------------------------------------------------+
| File/Directory          | Description                                                          |
+=========================+======================================================================+
| conversion_datatable    | Tabulated file, first column is the UNIQUE-ID in MetaCyc/MetaNetX    |
+-------------------------+----------------------------------------------------------------------+
| logs                    | Directory provides more detailed information                         |
+-------------------------+----------------------------------------------------------------------+

.. note::

  The ``conversion_datatable`` file acts as a bridge between the metabolomic data and the metabolic networks.
  It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``complementary_datatable`` file.
  This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite, and match them between the input metabolomic data and the metabolic networks.
  By leveraging both the MetaCyc/MetaNetX database and user-provided knowledge, the ``conversion_datatable`` enables robust and flexible mapping across diverse data sources.

  The ``logs`` directory contains detailed information about the processing steps.  
  It is useful for debugging, auditing, and understanding how the tool performed the mapping and handled the input data.


Output data details for database building mode are below in :doc:`inp_out_mapping`: *Datatable_conversion_metacyc* and *Datatable_conversion_metanetx*

