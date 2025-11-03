Overview
========

General description
-------------------

[MetaNetMap](https://github.com/coraliemuller/metanetmap) is a Python tool dedicated to mapping metabolite information between metabolomic data and metabolic networks.
The goal is to facilitate the identification of metabolites from **metabolomics data** that are also present in one or more **metabolic networks**, taking into consideration that data from the former has distinct identifier from the latter.

.. image:: ./pictures/MetaNetMap_overview.png
   :alt: General overview of MetaNetMap
   :width: 100%

Some metabolites can be rather easily identifiable using intermediate well-known identifiers, whereas for others, mapping is more difficult and may require partial matching. The picture below summarises the mapping procedure implemented in MetaNetMap. 


Why using this tool to map metabolomic data?
--------------------------------------------

- **ID variability in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools often assigns different IDs to the same metabolites. It is likely that those do not match the nomenclature of metabolomic annotations. To reconcile them, metadata from metabolic networks associating molecules to alternative databases can be used, so can third-party external databases such as [https://www.metanetx.org](MetaNetX). MetaNetMap provides such functionalities. 

- **Metabolomic data complexity:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified because they are indistinguishable by LC/MS methods. Matching must account for this.

MetaNetMap can match one or several metabolomic annotation tables to one or several metabolic networks. 

Third-party database for matching
---------------------------------

In case metadata from metabolic network do not match identifiers of the metabolomic data, a third-party database, referred to as *conversion_datatable* file acts as a bridge between the metabolomics data and the metabolic networks.  

MetaNetMap enables the construction of such resource using MetaNetX or MetaCyc knowledge bases. In the former case, data from ``chem_xref.tsv`` and ``chem_prop.tsv`` MetaNetX files is used. In the latter case (requires a licence), metadata from the ``compounds.dat`` file is extracted. Additionally, users can provide another table with existing mapping data, referred to as *datatable_complementary*.
  
The resulting table serves as a comprehensive knowledge base that allows MetaNetMap to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  

Refer to the documentation to build your first mapping table, using MetaNetX data.


.. note::
   The ``test`` commands of MetaNetMap rely on MetaCyc database.  
   However, complete information from MetaCyc related to the ontology of metabolites and pathways is **not included** in the test option because of licensing restrictions.  
   Only a simplified example (a "toy" version) of the ``datatable_conversion`` file is provided.


After building this knowledge base - ``datatable_conversion``, it is possible to perform mapping in several ways

- **Classic mode**:
The classic mode allows you to input one metabolomic data file or a directory containing several of them, and a unique metabolic network.

- **Community mode**:
The "community" mode allows you to input a directory containing one or several metabolomic data files, as well as a directory containing multiple metabolic networks.

- **Partial match (Option for mode classic and community)**:
The **partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).


Overview of the procedure
-------------------------

Pre-process mapping:
---------------------------------

  For **metabolomic data**, whether provided as single or multiple files, the data will be grouped by the column names of their identifiers such as ``unique-id``, ``common-name``, etc. This allows verification in the output file of which column the metabolite matched on.

  For **metabolic network data**, we typically extract the ID and name, as well as all possible metadata present in the networks for exemple: (chebi,InChIKey...).

  Using these two knowledge tables along with the ``datatable_conversion``, we test for matches as follows:


Mapping procedure
---------------------------------

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

.. note::
   If the partial match mode is activated, processing steps are applied on the three knowledge tables (enantiomers, CHEBI, etc.), and then all the previous steps are repeated.  
   CHEBI/ InChIKey processing is only done if present in the metabolomic data table.


Partial match 
---------------------------------
After this processing step, the entire mapping pipeline is re-executed, taking the modifications into account.

**The following treatments are applied:**

- **CHEBI** *(only if a CHEBI column exists in the metabolomics data)*:  
  For each row containing a CHEBI ID, the API of EBI is used to retrieve the full CHEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **INCHIKEY**:  
  An INCHIKEY is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract only this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomic data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomic datasets.



License
-------

GNU Lesser General Public License v3 (LGPLv3)

Authors
-------

Coralie Muller, `Sylvain Prigent <https://bfp.bordeaux-aquitaine.hub.inrae.fr/personnel/pages-web-personnelles/prigent-sylvain>`__  and `Clémence Frioux <https://cfrioux.github.io>`__ -- `Inria Pleiade team <https://team.inria.fr/pleiade/>`__
