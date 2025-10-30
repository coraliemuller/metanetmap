Application details
===================
MetaNetMap aims to map metabolites between metabolomic data and metabolic networks.

There are several challenges to this task:

- **ID homogenization in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools often assigns different IDs to the same metabolites. This inconsistency makes it difficult to cross-compare or transfer data across networks.

- **Metabolomic data complexities:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified as they are generally indistinguishable by standard LC–MS methods.

Successfully bridging metabolomic data and metabolic networks is complex but highly valuable, both for species-specific studies and community-level analyses.

Metanetmap enables this bridging process. We have developed a tool that primarily allows the construction of a knowledge base based on:

The ``datatable_conversion`` file acts as a bridge between the metabolomics data and the metabolic networks.  
It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``datatable_complementary`` file.  
This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  
By leveraging both the MetaCyc/MetaNetX database and user-provided enhancements, the ``datatable_conversion`` enables robust and flexible mapping across diverse data sources.

.. note::
   The test option is designed to work with the MetaCyc database.  
   However, information from MetaCyc related to the ontology of metabolites and pathways  
   is **not included** in the test option.  
   Only a simplified example (a "toy" version) of the ``datatable_conversion`` file is provided.


After building this knowledge base - ``datatable_conversion``, it is possible to perform mapping in several ways:

- **Classic mode**:
The classic mode allows you to input a single metabolomics data file and a directory containing multiple metabolic networks.

- **Community mode**:
The "community" mode allows you to input a directory containing multiple metabolomics data files, as well as a directory containing multiple metabolic networks.

- **Partial match (Option for mode classic and comminity)**:
The **partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).

After this processing step, the entire mapping pipeline is re-executed, taking the modifications into account.

**The following treatments are applied:**

- **CHEBI** *(only if a CHEBI column exists in the metabolomics data)*:  
  For each row containing a CHEBI ID, the API of EBI is used to retrieve the full CHEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **INCHIKEY**:  
  An INCHIKEY is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract only this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomic data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomic datasets.



**Pre-process mapping:**
  For **metabolomic data**, whether provided as single or multiple files, the data will be grouped by the column names of their identifiers such as ``unique-id``, ``common-name``, etc. This allows verification in the output file of which column the metabolite matched on.

  For **metabolic network data**, we typically extract the ID and name, as well as all possible metadata present in the networks for exemple: (chebi,InChIKey...).

  Using these two knowledge tables along with the ``datatable_conversion``, we test for matches as follows:


**Procedure:**
- **Step 1: Match metadata of networks with metabolomic data**  
  We first test for direct matches between the ids in metabolimic data and all the metadata in metabolomic networks without going through the ``datatable_conversion`` table to limit exchanges. 
  At the same time, for those that match, we verify if they have a unique ID in ``datatable_conversion``.
  
- **Step 2: Metabolomic data vs. ``datatable_conversion``**  
  Those that did not match in the previous step will be tested here. Duplicate checks will be performed, since multiple columns will be tested for the same metabolite (i.e., within a single row), it is possible that several identifiers for the same metabolite match. In this case, the matches will be merged into the same cell, separated by AND.

  If one of the identifiers does not match, but another identifier in the same row does, the non-matching one will be excluded from the output table.

  When partial match mode is **disabled**, the tool only uses the unique ID (e.g., MetaCyc/MetaNetX UNIQUE-ID) to determine whether a metabolite from the input data matches one from the reference database.
  In cases where two or more metabolites from the input potentially correspond to the same unique ID, this situation is flagged as a partial match. 
  The tool does not attempt to resolve this conflict automatically.
  Instead, these entries are explicitly marked so the user can manually review the potential ambiguity. This ensures data integrity and allows the user to decide whether:
 - The match is correct and can be accepted;

 - The mapping should be adjusted or ignored;

 - Further curation is needed (e.g., manual verification against synonyms, names, or external identifiers).

  This behavior helps avoid/reduce false positives during automatic matching.

- **Step 3: Match metabolites in ``datatable_conversion`` vs. network metadata**  
  For those identified with a match in step 2, we retrieve all their identifiers present in the network metadata and check if any of them match the network metadata.

  If none of the identifiers in the row match any reference, they will still be merged into a single cell in the result file, as they represent the same metabolite. 
  This allows all information for one metabolite to be grouped on a single row, improving clarity and readability.


If the partial match mode is activated, processing steps are applied on the three knowledge tables (enantiomers, CHEBI, etc.), and then all the previous steps are repeated.  
*Note:* CHEBI/ InChIKey processing is only done if present in the metabolomic data table.
