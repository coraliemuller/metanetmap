.. This file is included from input_data.rst

Input data details
==================

- **Structure** 
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
    metacyc_compounds.dat (MetaCyc)
    chem_xref.tsv (MetaNetX)
    chem_prop.tsv (MetaNetX)
    complementary_datatable.tsv (for MetaCyc/MetaNetX)
    datatable_conversion.tsv
    logs/


Input files for third-party database building mode
---------------------------------------

- **metacyc_compounds (MetaCyc)**:  
``compounds.dat`` has to be provided by the user. Access to this file requires a licence for MetaCyc

The following is a raw entry for the compound **WATER** from a MetaCyc flat file `.dat` extension. 
The file is structured as key-value pairs, where each line represents a specific property or annotation of the compound.

Some keys, such as `CHEMICAL-FORMULA`, `SYNONYMS`, or `DBLINKS`, may occur multiple times. Values can contain nested content, quotes, or formatting(e.g. HTML tags in names).

Some Key Characteristics (non-exhaustive)

| **Field**                | **Description**                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| `UNIQUE-ID`              | Primary identifier of the compound in the MetaCyc database.                                            |
| `TYPES`                  | Declares the type of entity — typically `Compound`, but can also be other biological entities.         |
| `COMMON-NAME`            | Human-readable compound name. May contain HTML formatting.                                             |
| `CHEMICAL-FORMULA`       | Chemical composition split across multiple lines, each specifying an element and its count.            |
| `DBLINKS`                | Cross-references to external databases such as BiGG, ChEBI, HMDB, KEGG, PubChem, etc. Multiple lines.  |
| `INCHI`                  | Standard InChI string describing the molecular structure.                                              |
| `INCHI-KEY`              | Hashed InChI identifier (short, fixed-length string) used for quick comparison of chemical structures. |
| `INSTANCE-NAME-TEMPLATE` | A template indicating how this compound ID is generated or structured (e.g., starts with `CPD-`).      |
| `LOGP`                   | Octanol–water partition coefficient (logP), representing hydrophobicity.                               |
| `MOLECULAR-WEIGHT`       | Average molecular weight based on atomic composition.                                                  |
| `MONOISOTOPIC-MW`        | Exact mass using the most abundant isotope for each element.                                           |
| `NON-STANDARD-INCHI`     | Alternative or non-standard InChI representation.                                                      |
| `POLAR-SURFACE-AREA`     | Topological polar surface area (TPSA) of the molecule.                                                 |
| `SMILES`                 | Simplified Molecular Input Line Entry System (SMILES) string representing the structure.               |
| `SYNONYMS`               | Alternate or common names for the compound. Can appear on multiple lines.                              |


Example Compound Entry in the MetaCyc file
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
- Tabular file provided by the user from MetaNetX website. It can also be directly downloaded by MetaNetMap using the command:
  
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

Example Entries
---------------

.. code-block:: text
  Source    ID      description
   BIOMASS BIOMASS BIOMASS
   mnx:BIOMASS     BIOMASS BIOMASS
   seedM:cpd11416  BIOMASS Biomass
   MNXM01  MNXM01  PMF||Translocated proton that accounts for the Proton Motive Force
   CHEBI:16234     MNXM02  hydroxide||HO-||Hydroxide ion||OH(-)||hydridooxygenate(1-)

Notes
-----

- The ``||`` separator indicates multiple synonyms or alternative names.
- Identifiers such as ``MNXM##`` correspond to MetaNetX universal metabolite IDs.
- Lines describing ``BIOMASS`` or ``PMF`` represent pseudo-metabolites used in
  metabolic network models.



- **chem_prop.tsv (MetaNetX):

This table lists basic information for metabolites or pseudo-metabolites,
including chemical formulas, charges, molecular masses, and structure encodings.
It links each metabolite to a reference identifier from a source database.

This file does not have to be provided by the user if MetaNetMap is used to download the necessary data, with the command:
  
  .. code-block:: bash

      metanetmap build_db --db metanetx

Table Structure
---------------

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

Example Entries
---------------

.. code-block:: text

   BIOMASS BIOMASS mnx:BIOMASS
   MNXM01  PMF     mnx:PMF H       1       1.00794 InChI=1S/p+1    GPRLSGONYQIRFK-UHFFFAOYSA-N     [H+]
   MNXM02  OH(-)   mnx:HYDROXYDE   HO      -1      17.00700        InChI=1S/H2O/h1H2/p-1   XLYOFNOQVPJJNP-UHFFFAOYSA-M     [H][O-]
   MNXM03  H3O(+)  mnx:OXONIUM     H3O     1       19.02300        InChI=1S/H2O/h1H2/p+1   XLYOFNOQVPJJNP-UHFFFAOYSA-O     [H][O+]([H])[H]

Notes
-----

- Some entries (like ``BIOMASS`` or ``PMF``) represent pseudo-metabolites used
  in constraint-based metabolic models.
- ``InChI`` and ``SMILES`` are standard line notations for representing chemical
  structures computationally.
- Charges and masses are provided for use in biochemical simulations and model
  balancing.


- **complementary_datatable**:  
  Tabular file provided by the user

(MetaCyc)
+-----------------+-------------------------------------+------+------+
| UNIQUE-ID       | ADD-COMPLEMENT                      | BIGG | SEED |
+=================+=====================================+=============+
| CPD-7100        | (2S)-2-isopropyl-3-oxosuccinic acid |      |      |
| DI-H-OROTATE    | (S)-dihydroorotic acid              |      |      |
| SHIKIMATE-5P    | 3-phosphoshikimic acid              |      |      |
| DIAMINONONANOATE| 7,8-diaminononanoate                | dann |      |
+-----------------+-------------------------------------+------+------+


(MetaNetX)
+-----------------+-------------------------------------+------+------+
| UNIQUE-ID       | ADD-COMPLEMENT                      | BIGG | SEED |
+=================+=====================================+=============+
| MNXM1602        | (2S)-2-isopropyl-3-oxosuccinic acid |      |      |
| MNXM252         | (S)-dihydroorotic acid              |      |      |
| MNXM1265        | 3-phosphoshikimic acid              |      |      |
| MNXM1140        | 7,8-diaminononanoate                | dann |      |
+-----------------+-------------------------------------+------+------+

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


Output data details for database building mode 
----------------------------------------------

Below in **Input Files for Mapping Mode**: Datatable_conversion_metacyc and Datatable_conversion_metanetx

Input files for mapping mode
---------------------------------------

- **metabolomic_data**:  
  .. note::
  For **metabolomic_data**:
  Column names must follow a specific naming convention and each line is a metabolite.
  Metabolomic data files must include column names that follow a specific naming convention in order to be properly processed by the tool during the mapping step.
 
  The following column names are recognized:

     ``UNIQUE-ID``, ``CHEBI``, ``COMMON-NAME``, ``ABBREV-NAME``, ``SYNONYMS``,
   ``ADD-COMPLEMENT``, ``MOLECULAR-WEIGHT``, ``MONOISOTOPIC-MW``, ``SEED``,
   ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC``, ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``,
   ``CAS``, ``INCHI-KEY``, ``SMILES``

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

- **Metabolic networks**: 

Metabolite information is represented in SBML (Systems Biology Markup Language) format.
An example of a metabolite entry in SBML format is shown below.

.. code-block:: [langage]
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

| Element              | Description                                                                   |
|----------------------|-------------------------------------------------------------------------------|
| `species`            | Defines a metabolite within a compartment                                     |
| `annotation`         | Contains **metadata** in RDF format, including standardized cross-references  |
| `chebi` / `inchikey` | Links to standardized identifiers for interoperability                        |



- **Datatable_conversion_MetaCyc**: 
Depending on the selected mode (``metanetx`` or ``metacyc``), the output file name will include the third-party knowledge base as a prefix.

- Some Column Name are missing (non-exhaustive)
+---------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+
|   UNIQUE-ID   | CHEBI  |      COMMON-NAME      | ABBREV-NAME |                                                                 SYNONYMS                                                                  | ADD-COMPLEMENT | MOLECULAR-WEIGHT | MONOISOTOPIC-MW | SEED |  BIGG  |
+===============+========+=======================+=============+===========================================================================================================================================+================+==================+=================+======+========+
|   CPD-17257   | 30828  |    trans-vaccenate    |             | ["trans-vaccenic acid", "(E)-octadec-11-enoate", "(E)-11-octadecenoic acid", "trans-11-octadecenoic acid", "trans-octadec-11-enoic acid"] |                |     281.457      | 282.2558803356  |      |        |
|   CPD-24978   | 50258  | alpha-L-allofuranose  |             |                                                                                                                                           |                |     180.157      | 180.0633881178  |      |        |
|   CPD-25014   | 147718 | alpha-D-talofuranoses |             |                                                                                                                                           |                |     180.157      | 180.0633881178  |      |        |
|   CPD-25010   | 153460 | alpha-D-mannofuranose |             |                                                                                                                                           |                |     180.157      | 180.0633881178  |      |        |
| Glucopyranose |  4167  |    D-glucopyranose    |             |                                           ["6-(hydroxymethyl)tetrahydropyran-2,3,4,5-tetraol"]                                            |                |     180.157      | 180.0633881178  |      | glc__D |
+---------------+--------+-----------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------------------+----------------+------------------+-----------------+------+--------+


==================  ================================================================================================================================
Column Name         Description
==================  ================================================================================================================================
UNIQUE-ID           The unique identifier for the compound, typically from the MetaCyc database (e.g., ``CPD-17257``).
CHEBI               The corresponding ChEBI identifier (if available), used for chemical standardization and interoperability.
COMMON-NAME         The common name of the metabolite as found in MetaCyc or other databases.
ABBREV-NAME         Abbreviated name for the metabolite, if defined. Often used in metabolic modeling tools (e.g., COBRA models).
SYNONYMS            A list of alternative names for the metabolite. These may include IUPAC names, trivial names, and other variants used in the literature/databases.
ADD-COMPLEMENT      Reserved for additional manually added metadata or complement terms, if applicable.
MOLECULAR-WEIGHT    The molecular weight (nominal or average) of the metabolite.
MONOISOTOPIC-MW     The monoisotopic molecular weight — i.e., the exact mass based on the most abundant isotope of each element.
SEED                Identifier from the SEED database, if available.
BIGG                Identifier from the BiGG Models database, if available. Typically used in genome-scale metabolic models.
HMDB                Identifier from the Human Metabolome Database (HMDB), if available.
METANETX            Identifier from the MetaNetX database, if available. This field becomes the unique identifier in this dataset.
LIGAND-CPD          Identifier from the KEGG Ligand Compound database (KEGG COMPOUND).
REFMET              Identifier from the RefMet metabolite reference list, used in metabolomics.
PUBCHEM             PubChem Compound Identifier (CID), if available.
CAS                 Chemical Abstracts Service (CAS) Registry Number, if available.
INCHI               IUPAC International Chemical Identifier string describing the compound structure.
NON-STANDARD-INCHI  A non-standardized or modified InChI representation, if applicable.
INCHI-KEY           The hashed InChIKey string derived from the InChI for compact referencing.
SMILES              Simplified Molecular Input Line Entry System (SMILES) string representing the compound’s structure.
==================  ================================================================================================================================

- **Datatable_conversion_metanetx**: 
Depending on the selected mode (``metanetx`` or ``metacyc``), the output file name will include the knowledge base as a prefix.

- Some Column Name are missing (non-exhaustive)
+---------------+--------------+----------------+------------------+----------------+------+--------+
|   UNIQUE-ID   |     CHEBI    | ADD-COMPLEMENT | MOLECULAR-WEIGHT | METACYC        | SEED |  BIGG  |
+===============+==============+================+==================+================+======+========+
|  MNXM1372018  | chebi:30828  |                |     281.457      | CPD-17257      |      |        |
|   MNXM41337   | chebi:50258  |                |     180.157      | CPD-24978      |      |        |
|  MNXM1113433  | chebi:147718 |                |     180.157      | CPD-25014      |      |        |
|  MNXM1117556  | chebi:153460 |                |     180.157      | CPD-25010      |      |        |
|  MNXM1364061  |  chebi:4167  |                |     180.157      | Glucopyranose  |      | glc__D |
+---------------+--------------+----------------+------------------+-----------------+------+--------+


Use the same description for the columns as above, except for the exceptions below, and make METANTX the unique identifier.

| Column Name        | Description                                                                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UNIQUE-ID`        | The unique identifier for the compound, typically from the MetaNetX database (e.g., `CPD-17257`).                                                  |                                         |
| `METACYC`          | Identifier from the METACYC database, if available. (exchanged with METANETX)  
| `VMH`              | Identifier from the VMH database, if available.                                                                                               |



Output data details
------------------


- **mapping_results**:  
  .. note::

The name of the output file depends on the processing mode:

- In **community mode**, the file is named as: ``community_mapping_results_YYYY-MM-DD_HH_MM_SS.tsv``
- In **classic mode**, the file is named as: ``mapping_results_YYYY-MM-DD_HH_MM_SS.tsv``
- If **partial match** is activated, the filename will include ``partial_match`` to indicate this.

**File content and column structure**

The output is a tabular file containing several columns with mapping results and metadata:

1. **Metabolite Matches**  
   Lists the metabolite IDS that matched.  
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
     - 
- **mapping_results**:
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


Output File Content and Column Structure
------------------
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Column Name**               | **Description**                                                                                                                                                                                                                                                            |
+===============================+============================================================================================================================================================================================================================================================================+
| `Metabolite`                  | Name of the input metabolite (from the experimental data). May be a name, SMILES, InChIKey, or identifier. If multiple matches are found, they are joined with "\_AND\_".                                                                                                  |
| `Match in database`           | Main match found in the reference database (e.g., MetaCyc/MetaNetX). May be a MetaCyc/MetaNetX ID like `CPD-XXXX` or a named entity. Multiple matches are joined with "\_AND\_" and flagged in **Partial Match**.                                                                            |
| `Match in metabolic networks` | List of metabolite matches in the metabolic network (SBML model). Typically uses short IDs like `met__L`. Returned as a list: `['met__L']`. In community mode, the list indicates each SBML model where the metabolite is present. The name is in the log for more details |
| `Partial match`               | Shows ambiguous or post-processed matches, e.g.: <br> - Duplicates <br> - CHEBI ontology expansion <br> - INCHIKEY simplification <br> - Enantiomer removal                                                                                                                |
| `Match via UNIQUE-ID`         | Indicates whether a match was found using the MetaCyc/MetaNetX `UNIQUE-ID` from the `datatable_conversion`. Displays `YES` if matched.                                                                                                                                              |
| `Match via CHEBI`             | Match based on **ChEBI** identifier. Displays `YES` if a ChEBI ID in the data matched the network.                                                                                                                                                                         |
| `Match via COMMON-NAME`       | Match based on common (non-abbreviated) name of the metabolite. E.g., `"methionine"`.                                                                                                                                                                                      |
| `Match via ABBREV-NAME`       | Match based on abbreviated names, often from SBML or COBRA models. E.g., `"met__L"`, `"pnto__R"`.                                                                                                                                                                          |
| `Match via SYNONYMS`          | Match using any of the listed synonyms for the metabolite. Useful when matching trivial or alternate names.                                                                                                                                                                |
| `Match via ADD-COMPLEMENT`    | Match using manually added complementary fields (from `ADD-COMPLEMENT` column in your input data).                                                                                                                                                                         |
| `Match via BIGG`              | Match using **BiGG Models** identifiers. Typically abbreviated and used in genome-scale models.                                                                                                                                                                            |
| `Match via HMDB`              | Match via **Human Metabolome Database (HMDB)** identifiers.                                                                                                                                                                                                                |
| `Match via METANETX`          | Match via **MetaNetX** IDs, used for cross-database integration.                                                                                                                                                                                                           |
| `Match via LIGAND-CPD`        | Match via identifiers from **KEGG Ligand** or other ligand-based databases.                                                                                                                                                                                                |
| `Match via REFMET`            | Match via **RefMet**, a reference nomenclature system for metabolomics.                                                                                                                                                                                                    |
| `Match via PUBCHEM`           | Match via **PubChem Compound IDs (CIDs)**.                                                                                                                                                                                                                                 |
| `Match via CAS`               | Match using **CAS numbers** (Chemical Abstracts Service).                                                                                                                                                                                                                  |
| `Match via INCHI-KEY`         | Match based on the **InChIKey**, a hashed version of the InChI chemical identifier.                                                                                                                                                                                        |
| `Match via SMILES`            | Match via the **SMILES** string (Simplified Molecular Input Line Entry System) representing the molecular structure.                                                                                                                                                       |
| `Match via FORMULA`           | Match based on **molecular formula**, e.g., `C6H12O6`.                                                                                                                                                                                                                     |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+




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