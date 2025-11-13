==============
Advanced usage
==============


UNIQUE-ID
----------

The UNIQUE-ID is defined as the primary identifier for a specific metabolite.

It represents the unique reference assigned to each metabolite in the database used to generate the conversion datatable (e.g., MetaCyc:Glucopyranose, MetaNetX:MNXM1364061, etc.). It also serves as the central reference point to which all other identifiers related to this metabolite, such as InChI, COMMON-NAME, ChEBI, ... are linked.

In both the third-party database and the complementary datatable, the UNIQUE-ID must appear as the first column. This ensures consistency, as the identifier uniquely facilitates data validation and matching across different sources, with all complementary information related to a metabolite linked to it.

Therefore, the UNIQUE-ID serves as the central reference point for detecting potential ambiguities between datasets and for eliminating redundancies.



Creating your own Third-party database
---------------------------------------

**Requirements and structure:**

- The **first column must be** a ``UNIQUE-ID`` that links to the MetaCyc/MetaNetX database or your own unqiue identifiers.

- All following columns normally follow the column names listed below, but you can add others with different names if needed.

- It is recommended to keep the columns ``ChEBI``, ``PUBCHEM``, and ``InChIKey`` with the same names, as Metanetmap performs a preprocessing step to check that they contain the correct prefixes (ChEBI:, PUBCHEM:, or InChIKey=) and adds them if necessary., If the columns do not have the correct name, this preprocessing will not be performed.

- For ``SYNONYMS``, the synonyms column also undergoes preprocessing, since in our data tables, the expected syntax is a list: ['synonym1', 'synonym2']. If you want to include synonyms, please use this syntax.

- The file must be in tabular format (e.g., TSV), with headers.

  .. note::
    The following column names are recognised:

    ``UNIQUE-ID``, ``ChEBI``, ``COMMON-NAME``, ``ABBREV-NAME``, ``SYNONYMS``, ``ADD-COMPLEMENT``, ``MOLECULAR-WEIGHT``, ``MONOISOTOPIC-MW``, ``SEED``,
    ``BIGG``, ``HMDB``, ``METANETX``, ``METACYC``, ``LIGAND-CPD``, ``REFMET``, ``PUBCHEM``, ``CAS``, ``InChIKey``, ``SMILES``




Partial match
---------------

**Partial match** is an option to the mapping mode that aims at rescuing unmatched entries. Note that it can be time-consuming depending on the number of unmatched metabolite signals. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via ChEBI, InChIKey, or enantiomer simplification).

After this processing step, the entire mapping pipeline is re-executed, taking the modifications into account.

**The following treatments are applied:**

- **ChEBI** *(only if a ChEBI column exists in the metabolomics data)*:  
  For each row containing a ChEBI ID, the API from EBI is used to retrieve the full ChEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **InChIKey**:  
  An InChIKey is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract only this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomics data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomics datasets.

To facilitate the analysis of the results, every match found during this process will be automatically added to the "Partial match" column in the output. 
The user should be cautious when using these matches, as they require manual validation before any interpretation.


Handling Ambiguities
--------------------

Using a large amount of cross-referenced data increases the probability that inconsistent mappings will occur and, consequently, the risk of ambiguity. The same metabolite may match multiple times in the conversion datatable, in the metabolomic data, or in the metabolic networks.

The tool checks for potentially conflicting matches using only the unique identifier (e.g., the MetaCyc or MetaNetX *UNIQUE-ID*) to determine whether a metabolite from the input data corresponds to one or more metabolites in the reference database. 

When multiple input metabolites correspond to the same unique identifier — or vice versa — this situation is flagged as an ambiguity and is automatically added to the *"Partial match"* column in the output.

The tool does not attempt to resolve this conflict automatically.
Instead, these entries are explicitly marked, so the user can manually review and resolve the ambiguity. This ensures data integrity and allows the user to decide whether:

- The match is correct and can be accepted;

- The mapping should be adjusted or ignored;

- Further curation is needed (e.g., manual verification against synonyms, names, or external identifiers).

This behaviour helps avoid/reduce false positives during automatic matching.


.. note::
    A new version with enhanced ambiguity management will be released soon. It will improve the handling of identifiers that are particularly prone to duplication, such as COMMON-NAME and InChI.
    
    It should be noted that the effectiveness of ambiguity handling may vary depending on the structure of the data, whether they are metabolic datasets, metabolic networks, or conversion tables.
    
    For example, although the InChI is theoretically unique for a single metabolite, in practice, some databases or metabolic networks may associate one InChI with multiple metabolites, which introduces ambiguity.
    
    Similarly, in metabolomic data, certain columns may combine or concatenate several types of identifiers. This can reduce the likelihood of accurate matching, as the identifiers are not clearly separated. Specific preprocessing steps are implemented, for example, adding prefixes to identifiers such as PUBCHEM or ChEBI to standardize IDs and prevent conflicts between numeric values, ultimately improving comparison accuracy.