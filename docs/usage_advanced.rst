=====
Usage Advanced
=====


**UNIQUE-ID:**
--------------------

The UNIQUE-ID column must always be the first column and represents the unique identifier for each metabolite identified in the database used to create the conversion table (e.g., MetaCyc:Glucopyranose, MetaNetX:MNXM1364061 , etc.).

This identifier is unique and facilitates data transfer and matching between different sources, as all complementary information related to a metabolite is associated with it. 

It therefore serves as the central link for detecting potential ambiguities between datasets and eliminating redundancies.



**Create your own Third-party database  :**
--------------------

   **Requirements and structure:**
   
   - The **first column must be** a ``UNIQUE-ID`` that links to the MetaCyc/MetaNetX database or your own unqiue identifiers.
   
   - All following columns normally follow the column names listed below, but you can add others with different names if needed.

   - It is recommended to keep the columns ``CHEBI``, ``PUBCHEM``, and ``INCHI-KEY`` with the same names, as Metanetmap performs a preprocessing step to check that they contain the correct prefixes (CHEBI:, PUBCHEM:, or InChIKey=) and adds them if necessary., If the columns do not have the correct name, this preprocessing will not be performed.

   - For ``SYNONYMS``, the synonyms column also undergoes preprocessing, since in our data tables, the expected syntax is a list: ['synonym1', 'synonym2']. If you want to include synonyms, please use this syntax.

   - The file must be in tabular format (e.g., TSV), with headers.
   
    .. note::
      The following column names are recognised:

       ``UNIQUE-ID``, ``CHEBI``, ``COMMON-NAME``, ``ABBREV-NAME``, ``SYNONYMS``, ``ADD-COMPLEMENT``, ``MOLECULAR-WEIGHT``, ``MONOISOTOPIC-MW``, ``SEED``,
       ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC``, ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``, ``CAS``, ``INCHI-KEY``, ``SMILES``




**Partial match:**
--------------------

The **partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).

After this processing step, the entire mapping pipeline is re-executed, taking the modifications into account.

**The following treatments are applied:**

- **CHEBI** *(only if a CHEBI column exists in the metabolomics data)*:  
  For each row containing a CHEBI ID, the API from EBI is used to retrieve the full CHEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **INCHIKEY**:  
  An INCHIKEY is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract only this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomics data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomics datasets.

To facilitate the analysis of the results, every match found during this process will be automatically added to the "Partial match" column in the output. 
The user should be cautious when using these matches, as they require manual validation before any interpretation.


**Handling Ambiguities:**
--------------------

 Using a large amount of cross-referenced data increases the number of matches for certain entries and, consequently, the risk of ambiguity. The same metabolite may match multiple times in the conversion table or in the metabolomics data, and this risk applies to all three types of data.

 The tool checks for potentially conflicting matches using only the unique identifier (e.g., the MetaCyc or MetaNetX *UNIQUE-ID*) to determine whether a metabolite from the input data corresponds to one or more metabolites in the reference database.

 When multiple input metabolites correspond to the same unique identifier—or vice versa—this situation is flagged as an ambiguity and is automatically added to the *"Partial match"* column in the output.


The tool does not attempt to resolve this conflict automatically.
Instead, these entries are explicitly marked, so the user can manually review and resolve the potential ambiguity. This ensures data integrity and allows the user to decide whether:
- The match is correct and can be accepted;

- The mapping should be adjusted or ignored;

- Further curation is needed (e.g., manual verification against synonyms, names, or external identifiers).

This behaviour helps avoid/reduce false positives during automatic matching.


.. note::
    A new version with broader ambiguity management will be released soon. It will handle, for example, identifiers that are most prone to duplication (such as *COMMON-NAME*, *InChI*, etc.).
    It should be noted that, depending on how the data are structured (metabolic data, GSMN, or conversion tables), ambiguities may be handled with varying levels of accuracy.


