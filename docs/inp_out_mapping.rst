
Inputs and outputs: Mapping mode
==========

**Note:** All input files are required to use tab characters as field delimiters.

Structure
------------------

 Example of directory structure (but files and directories can be placed anywhere):

  .. code-block:: text

    example:
    Metabolic_network_inputs
    ├── species_1.sbml
    ├── species_4.sbml
    ├── species_10.xml
    ├── ...

    maf_folder_input
    ├── species_1.tsv
    ├── species_4.tsv
    ├── species_10.tsv
    ├── ...
    datatable_conversion.tsv
    logs/



Input data
--------------

+---------------------+----------------------------------------------------------------------+
| File/Directory      | Description                                                          |
+=====================+======================================================================+
| MetaNetMap output   | Output directory for mapping results and logs                        |
+---------------------+----------------------------------------------------------------------+
| metabolic_networks  | Path to the directory with .sbml or/and .xml files                   |
+---------------------+----------------------------------------------------------------------+
| metabolomic_data   | Tabulated file, (cf note below for details)                           |
+---------------------+----------------------------------------------------------------------+
| conversion_datatable| Tabulated file, first column is the UNIQUE-ID in MetaCyc/MetaNetX    |
+---------------------+----------------------------------------------------------------------+



Details input files for mapping mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. toggle:: 

  -  **metabolomic_data**:
    Column names must follow a specific naming convention and each line is a metabolite.
    Metabolomic data files must include column names that follow a specific naming convention in order to be properly processed by the tool during the mapping step.
   
    .. note::
      The following column names are recognized:

       ``UNIQUE-ID``, ``CHEBI``, ``COMMON-NAME``, ``ABBREV-NAME``, ``SYNONYMS``, ``ADD-COMPLEMENT``, ``MOLECULAR-WEIGHT``, ``MONOISOTOPIC-MW``, ``SEED``,
       ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC``, ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``, ``CAS``, ``INCHI-KEY``, ``SMILES``


  - *Some Key Characteristics (non-exhaustive)*
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  | UNIQUE-ID  | CHEBI       | COMMON-NAME                        | M/Z          | INCHI-KEY                                 | 
  +============+=============+====================================+==============+===========================================+
  |            | CHEBI:4167  |                                    | 179          |                                           |
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  |            |             | L-methionine                       | 150          |                                           |        
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  | CPD-17381  |             | roquefortine C                     | 389.185      |                                           |        
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  |            |             |                                    |              | InChIKey=CGBYBGVMDAPUIH-ARJAWSKDSA-L      |
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  | CPD-25370  | 84783       |                                    | 701.58056    |                                           |
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  |            | CHEBI:16708 | Adenine                            |              |                                           |
  +------------+-------------+------------------------------------+--------------+-------------------------------------------+
  

  _________________________________________________________________________________________________________________________________


  - **Metabolic networks**: 
  
  Metabolite information is represented in SBML (Systems Biology Markup Language) format.
  An example of a metabolite entry in SBML format is shown below.

  .. code-block:: xml
     :linenos:
  
     <?xml version="1.0" encoding="UTF-8"?>
     <sbml xmlns="http://www.sbml.org/sbml/level3/version1/core"
           level="3" version="1">
       <model id="example_model" name="Example Metabolic Model">
         <!-- Compartments -->
         <listOfCompartments>
           <compartment id="cytosol" name="Cytosol" constant="true"/>
         </listOfCompartments>
  
         <listOfSpecies>
           <species id="glucose_c" name="Glucose" compartment="cytosol" initialAmount="1.0" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false">
             <annotation>
               <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                 <rdf:Description rdf:about="#glucose_c">
                   <bqbiol:is>
                     <rdf:Bag>
                       <rdf:li rdf:resource="http://identifiers.org/chebi/CHEBI:17234"/>
                       <rdf:li rdf:resource="http://identifiers.org/inchikey/WQZGKKKJIJFFOK-GASJEMHNSA-N"/>
                     </rdf:Bag>
                   </bqbiol:is>
                 </rdf:Description>
               </rdf:RDF>
             </annotation>
           </species>
         </listOfSpecies>
       </model>
     </sbml>
  

  
  For **metabolic network data**, we typically extract the ID and name, as well as all possible metadata present in the networks for exemple: (chebi,InChIKey...) via annotation.
  
  +--------------------------+------------------------------------------------------------------------------+
  | Element                  | Description                                                                  |
  +==========================+==============================================================================+
  | ``species``              | Defines a metabolite within a compartment                                    |
  +--------------------------+------------------------------------------------------------------------------+
  | ``annotation``           | Contains **metadata** in RDF format, including standardized cross-references |
  +--------------------------+------------------------------------------------------------------------------+

  
     _________________________________________________________________________________________________________________________________

  
  - **Datatable_conversion_MetaCyc**: 
  Depending on the selected mode (``metanetx`` or ``metacyc``), the output file name will include the third-party knowledge base as a prefix.
  
  - Some Column Name are missing (non-exhaustive)
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
   | **UNIQUE-ID**   | CHEBI  |      COMMON-NAME      | ABBREV-NAME |                                                                 SYNONYMS                                                                  | ADD-COMPLEMENT | MOLECULAR-WEIGHT | MONOISOTOPIC-MW | SEED |  BIGG  |
   +=================+========+=======================+=============+===========================================================================================================================================+================+==================+=================+======+========+
   | CPD-17257       | 30828  | trans-vaccenate       |             | ["trans-vaccenic acid", "(E)-octadec-11-enoate", "(E)-11-octadecenoic acid", "trans-11-octadecenoic acid", "trans-octadec-11-enoic acid"] |                | 281.457          | 282.2558803356  |      |        |
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
   | CPD-24978       | 50258  | alpha-L-allofuranose  |             |                                                                                                                                           |                | 180.157          | 180.0633881178  |      |        |
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
   | CPD-25014       | 147718 | alpha-D-talofuranoses |             |                                                                                                                                           |                | 180.157          | 180.0633881178  |      |        |
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
   | CPD-25010       | 153460 | alpha-D-mannofuranose |             |                                                                                                                                           |                | 180.157          | 180.0633881178  |      |        |
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
   | Glucopyranose   | 4167   | D-glucopyranose       |             | ["6-(hydroxymethyl)tetrahydropyran-2,3,4,5-tetraol"]                                                                                      |                | 180.157          | 180.0633881178  |      | glc__D |
   +-----------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+

  - Description
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | Column Name       | Description                                                                                                                                        |
   +===================+====================================================================================================================================================+
   | UNIQUE-ID         | The unique identifier for the compound, typically from the MetaCyc database (e.g., ``CPD-17257``).                                                 |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | CHEBI             | The corresponding ChEBI identifier (if available), used for chemical standardization and interoperability.                                         |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | COMMON-NAME       | The common name of the metabolite as found in MetaCyc or other databases.                                                                          |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | ABBREV-NAME       | Abbreviated name for the metabolite, if defined. Often used in metabolic modeling tools (e.g., COBRA models).                                      |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | SYNONYMS          | A list of alternative names for the metabolite. These may include IUPAC names, trivial names, and other variants used in the literature/databases. |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | ADD-COMPLEMENT    | Reserved for additional manually added metadata or complement terms, if applicable.                                                                |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | MOLECULAR-WEIGHT  | The molecular weight (nominal or average) of the metabolite.                                                                                       |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | MONOISOTOPIC-MW   | The monoisotopic molecular weight — i.e., the exact mass based on the most abundant isotope of each element.                                       |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | SEED              | Identifier from the SEED database, if available.                                                                                                   |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | BIGG              | Identifier from the BiGG Models database, if available. Typically used in genome-scale metabolic models.                                           |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | HMDB              | Identifier from the Human Metabolome Database (HMDB), if available.                                                                                |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | METANETX          | Identifier from the MetaNetX database, if available. This field becomes the unique identifier in this dataset.                                     |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | LIGAND-CPD        | Identifier from the KEGG Ligand Compound database (KEGG COMPOUND).                                                                                 |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | REFMET            | Identifier from the RefMet metabolite reference list, used in metabolomics.                                                                        |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | PUBCHEM           | PubChem Compound Identifier (CID), if available.                                                                                                   |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | CAS               | Chemical Abstracts Service (CAS) Registry Number, if available.                                                                                    |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | INCHI             | IUPAC International Chemical Identifier string describing the compound structure.                                                                  |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | NON-STANDARD-INCHI| A non-standardized or modified InChI representation, if applicable.                                                                                |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | INCHI-KEY         | The hashed InChIKey string derived from the InChI for compact referencing.                                                                         |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | SMILES            | Simplified Molecular Input Line Entry System (SMILES) string representing the compound’s structure.                                                |
   +-------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+


   - **Datatable_conversion_metanetx**: 
   Depending on the selected mode (``metanetx`` or ``metacyc``), the output file name will include the knowledge base as a prefix.
   
   - Some Column Name are missing (non-exhaustive)
   +---------------+--------------+----------------+------------------+-----------------+------+--------+
   |   UNIQUE-ID   |     CHEBI    | ADD-COMPLEMENT | MOLECULAR-WEIGHT | METACYC         | SEED |  BIGG  |
   +===============+==============+================+==================+=================+======+========+
   |  MNXM1372018  | chebi:30828  |                |     281.457      | CPD-17257       |      |        |
   |   MNXM41337   | chebi:50258  |                |     180.157      | CPD-24978       |      |        |
   |  MNXM1113433  | chebi:147718 |                |     180.157      | CPD-25014       |      |        |
   |  MNXM1117556  | chebi:153460 |                |     180.157      | CPD-25010       |      |        |
   |  MNXM1364061  |  chebi:4167  |                |     180.157      | Glucopyranose   |      | glc__D |
   +---------------+--------------+----------------+------------------+-----------------+------+--------+
   
   
   Use the same description for the columns as above, except for the exceptions below, and make METANTX the unique identifier.
   
   +-------------------+----------------------------------------------------------------------------------------------------+
   | Column Name       | Description                                                                                        |
   +===================+====================================================================================================+
   | UNIQUE-ID         | The unique identifier for the compound, typically from the MetaNetX database (e.g., ``CPD-17257``).|
   +-------------------+----------------------------------------------------------------------------------------------------+
   | METACYC           | Identifier from the METACYC database, if available. (exchanged with METANETX)                      |
   +-------------------+----------------------------------------------------------------------------------------------------+
   | VMH               | Identifier from the VMH database, if available.                                                    |
   +-------------------+----------------------------------------------------------------------------------------------------+

  

Output data
--------------

+-------------------------+-------------------------------------------------------------+
| File/Directory          | Description                                                 |
+=========================+=============================================================+
| mapping_results         | Tabulated file with match/unmatch results                   |
+-------------------------+-------------------------------------------------------------+
| logs                    | Directory provides more detailed information                |
+-------------------------+-------------------------------------------------------------+


.. toggle::

   **Output file format**
   
   The name of the output file depends on the processing mode:
   
   - In **community mode**, the file is named as: ``community_mapping_results_YYYY-MM-DD_HH_MM_SS.tsv`` 
   - In **classic mode**, the file is named as: ``mapping_results_YYYY-MM-DD_HH_MM_SS.tsv``
   - If **partial match** is activated, the filename will include ``partial_match`` to indicate the use of the option.
   
   
   **File content and column structure**
   
   The output is a tabular file containing several columns with mapping results and metadata:
   
   1. **Metabolite Matches** 
       
      Lists the metabolite names that matched.  
      If multiple matches are found for a single input (i.e., duplicates), they are joined using ``_AND_``.  
   
   2. **MetaCyc/MetaNetX UNIQUE-ID Match (from `conversion_datatable`)**  
      
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
   
   
   
   
   - Some Column Name are missing (non-exhaustive)
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | Metabolites                                        | Match in database    | Match in metabolic         | Partial match         | Match via UNIQUE-ID| Match via CHEBI |
   |                                                    |                      | networks                   |                       |                    |                 |
   +====================================================+======================+============================+=======================+====================+=================+
   | CPD-17381 _AND_ roquefortine C                     | CPD-17381            |                            | YES                   |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | 84783 _AND_ CPD-25370                              | CPD-25370            | ['toys1']                  |                       | YES                | YES             |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | C9H16NO5                                           |                      | ['toys3']                  | C9H16NO5              | YES                |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | 4167                                               | Glucopyranose        | ['toys1', 'toys3']         |                       |                    | YES             |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | L-methionine _AND_ methionine                      | MET                  | ['toys1', 'toys2', 'toys3']|                       |                    |                 |
   +----------------------------------------------------+----------------------+--------------------------+-------------------------+--------------------+-----------------+
   | 16708 _AND_ Adenine                                | ADENINE              | ['toys1', 'toys3']         |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | 8-O-methylfusarubin alcohol                        | CPD-18186            | ['toys2']                  |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | orotic acid                                        | OROTATE              | ['toys2', 'toys3']         |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | Carbamyl-phosphate                                 | CARBAMOYL-P          | ['toys2']                  |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | pantothenic acid                                   | PANTOTHENATE         | ['toys2', 'toys3']         |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | aprut                                              | CPD-569              |                            |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | f1p                                                | CPD-15970 _AND_ FRU1P| ['toys3']                  | CPD-15970 _AND_ FRU1P |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   | crnmock                                            |                      | ['toys3']                  |                       |                    |                 |
   +----------------------------------------------------+----------------------+----------------------------+-----------------------+--------------------+-----------------+
   
   
     
   - Output File Content and Column Structure
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Column Name**               | **Description**                                                                                                                                                                                                                                |
   +===============================+================================================================================================================================================================================================================================================+
   | ``Metabolite``                | Name of the input metabolite (from the experimental data). May be a name, SMILES, InChIKey, or identifier. If multiple matches are found, they are joined with ``_AND_``.                                                                      |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match in database``         | Main match found in the reference database (e.g., MetaCyc/MetaNetX). May be a MetaCyc/MetaNetX ID like ``CPD-XXXX`` or a named entity. Multiple matches are joined with ``_AND_`` and flagged in **Partial Match**.                            |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   |``Match in metabolic networks``| List of metabolite matches in the metabolic network (SBML model). Typically uses short IDs like ``['met__L']``. In community mode, the list indicates each SBML model where the metabolite is present. The name is in the log for more details.|
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Partial match``             | Shows ambiguous or post-processed matches, e.g.:                                                                                                                                                                                               |
   |                               | - Duplicates                                                                                                                                                                                                                                   |
   |                               | - CHEBI ontology expansion                                                                                                                                                                                                                     |
   |                               | - INCHIKEY simplification                                                                                                                                                                                                                      |
   |                               | - Enantiomer removal                                                                                                                                                                                                                           |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via UNIQUE-ID``       | Indicates whether a match was found using the MetaCyc/MetaNetX ``UNIQUE-ID`` from the ``datatable_conversion``. Displays ``YES`` if matched.                                                                                                   |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via CHEBI``           | Match based on **ChEBI** identifier. Displays ``YES`` if a ChEBI ID in the data matched the network.                                                                                                                                           |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via COMMON-NAME``     | Match based on common (non-abbreviated) name of the metabolite. E.g., ``methionine``.                                                                                                                                                          |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via ABBREV-NAME``     | Match based on abbreviated names, often from SBML or COBRA models. E.g., ``met__L``, ``pnto__R``.                                                                                                                                              |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via SYNONYMS``        | Match using any of the listed synonyms for the metabolite. Useful when matching trivial or alternate names.                                                                                                                                    |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via ADD-COMPLEMENT``  | Match using manually added complementary fields (from ``ADD-COMPLEMENT`` column in your input data).                                                                                                                                           |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via BIGG``            | Match using **BiGG Models** identifiers. Typically abbreviated and used in genome-scale models.                                                                                                                                                |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via HMDB``            | Match via **Human Metabolome Database (HMDB)** identifiers.                                                                                                                                                                                    |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via METANETX``        | Match via **MetaNetX** IDs, used for cross-database integration.                                                                                                                                                                               |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via LIGAND-CPD``      | Match via identifiers from **KEGG Ligand** or other ligand-based databases.                                                                                                                                                                    |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via REFMET``          | Match via **RefMet**, a reference nomenclature system for metabolomics.                                                                                                                                                                        |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via PUBCHEM``         | Match via **PubChem Compound IDs (CIDs)**.                                                                                                                                                                                                     |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via CAS``             | Match using **CAS numbers** (Chemical Abstracts Service).                                                                                                                                                                                      |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via INCHI-KEY``       | Match based on the **InChIKey**, a hashed version of the InChI chemical identifier.                                                                                                                                                            |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via SMILES``          | Match via the **SMILES** string (Simplified Molecular Input Line Entry System) representing the molecular structure.                                                                                                                           |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``Match via FORMULA``         | Match based on **molecular formula**, e.g., ``C6H12O6``.                                                                                                                                                                                       |
   +-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   
   


- **log**:

Provides more information about each step and the corresponding results.

.. code-block:: none

    -----------------------------------------
                MAPPING METABOLITES 
    ----------------------------------------- 

    ------ Main package version ------
    numpy version: 2.3.2
    pandas version: 2.3.2 
    cobra version: 0.29.1

    Command run:
    Actual command run (from sys.argv): python /home/cmuller/miniconda3/envs/test2/bin/metanetmap -t -c -p

    #---------------------------#
          Test COMMUNITY   
    #---------------------------#

     Test with Toys -  maf : "metanetmap/test_data/data_test/toys/maf" and "metanetmap/test_data/data_test/toys/sbml"

    ----------------------------------------------
    ---------------MATCH STEP 1-------------------
    ----------------------------------------------

    <1> Direct matching test between metabolites derived from metabolomic data on  all metadata in the metabolic network 
    <2> Matching test between metabolites derived from metabolomic data on all metadata in the database conversion

    ++ Match step for "CPD-17381":
    -- "CPD-17381" is present in database with the UNIQUE-ID "CPD-17381" and matches via "UNIQUE-ID"

    ++ Match step for "CPD-25370":
    -- "CPD-25370" is present directly in "toys1" metabolic network with the ID "CPD-25370" via "UNIQUE-ID"
    -- "CPD-25370" is present in database with the UNIQUE-ID "CPD-25370" and matches via "UNIQUE-ID"

    ++ Match step for "C9H16NO5":
    -- "C9H16NO5" is present directly in "toys3" metabolic network with the ID "pnto__R" via "UNIQUE-ID"
    -- ""C9H16NO5"" has a partial match. We have a formula as identifier for this metabolite: "C9H16NO5"

    ++ Match step for "4167":
    -- "4167" is present directly in "toys3" metabolic network with the ID "glc__D" via "CHEBI"
    .....

    --"NO" is present directly in metabolic network with the corresponding ID "NITRIC-OXIDE" via the match ID "nitric-oxide"


    ......

    ----------------------------------------------
    ---------------MATCH STEP 2-------------------
    ----------------------------------------------
    
    <3> Matching test on metabolites that matched only on the database conversion data against all metadata from the metabolic network
    
    --"Glycocholic acid" is present directly in metabolic network with the corresponding ID "GLYCOCHOLIC_ACID" via the match ID "glycocholic_acid"
    --"gamma-Tocopherol" is present directly in metabolic network with the corresponding ID "GAMA-TOCOPHEROL" via the match ID "gama-tocopherol"
    
    .......


    -------------------- SUMMARY REPORT --------------------


    Recap of Matches:
      + Matched metabolites: 103
      + Unmatched metabolites: 43740
      + Partial matches: 15
    
     Match Details:
      -- Full match (database + SBML): 103
      -- Partial match + metabolic info: 10
      -- Match only in SBML: 0
    
     Unmatch Details:
      -- Full unmatch (no match in DB or SBML): 43514
      -- Match in DB but not in SBML: 226
      -- Partial match in DB only: 5
    
    --------------------------------------------------------
    
    
    --- Total runtime 1478.55 seconds ---
     --- MAPPING COMPLETED'


