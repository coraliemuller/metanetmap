Overview
========

General description
-------------------

`MetaNetMap <https://github.com/coraliemuller/metanetmap>`_ is a Python tool dedicated to mapping metabolite information between metabolomic data and metabolic networks.
The goal is to facilitate the identification of metabolites from **metabolomic data** that are present in one or more **metabolic networks** to facilitate further modelling, taking into consideration that data from the former likely has distinct identifiers from the latter.

.. image:: ./pictures/MetaNetMap_overview.png
   :alt: General overview of MetaNetMap
   :width: 100%

While some metabolites can be matched directly using common identifiers, many require more sophisticated approaches. MetaNetMap implements such strategies to improve mapping rates, including optional partial matching techniques. The picture above summarises the mapping procedure implemented in MetaNetMap. 


Why using this tool to map metabolomic data?
--------------------------------------------

Mapping metabolomic data to metabolic networks is a challenging task for several reasons:

- **Identifier variability in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools and associated databases often assigns distinct identifiers to the same metabolites. It is likely that those do not match the nomenclature of metabolomic annotations. To reconcile them, a first solution is to rely on metadata extracted from metabolic networks associating molecules to alternative databases. Additionally, third-party external databases such as `MetaNetX <https://www.metanetx.org>`_ can be used, in order to provide more matching possibilities.  

- **Metabolomic data complexity:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified because they are indistinguishable by LC/MS methods. Matching must account for this.

While a few metabolites can be matched manually with limited effort, large-scale metabolomic datasets require automated tools to perform mapping efficiently and accurately. MetaNetMap addresses these challenges by providing a robust framework for mapping metabolomic data to metabolic networks, leveraging multiple strategies to maximize matching success. In practice, MetaNetMap can match one or several metabolomic annotation tables to one or several metabolic networks. 

Third-party database for matching
---------------------------------

In case metadata from metabolic network do not match identifiers of the metabolomic data, a third-party database, referred to as *conversion_datatable* file acts as a bridge between the metabolomic data and the metabolic networks.  

MetaNetMap enables the construction of such resource using MetaNetX or MetaCyc knowledge bases. In the former case, data from ``chem_xref.tsv`` and ``chem_prop.tsv`` MetaNetX files is used. In the latter case (requires a licence), metadata from the ``compounds.dat`` file is extracted. Additionally, users can provide another table with existing mapping data resulting from previous curation efforts for instance, referred to as *datatable_complementary*.
  
The conversion table serves as a comprehensive knowledge base that allows MetaNetMap to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  

Refer to the related documentation :doc:`usage` to build your first mapping table using MetaNetX data.

.. note::
   The ``test`` commands of MetaNetMap rely on MetaCyc database.  
   However, complete information from MetaCyc related to the ontology of metabolites and pathways is **not included** in the test option because of licensing restrictions.  
   Only a simplified example (a "toy" version) of the ``conversion_datatable`` file is provided. If you have a MetaCyc licence, you can build the complete conversion table using the ``compounds.dat`` file from MetaCyc database.


After building this knowledge base, mapping can be performed in two modes:

- **Classic mode**: The classic mode allows you to input one metabolomic data file or a directory containing several of them, and a unique metabolic network.

- **Community mode**: The "community" mode allows you to input a directory containing one or several metabolomic data files, as well as a directory containing multiple metabolic networks. It will map each metabolomic data file against each metabolic network file, resulting in a comprehensive mapping across all combinations. This mode is useful for large-scale analyses involving a microbial community where multiple organisms and their associated networks are considered in the metabolomic study.

▸ **Partial match (Option for mode classic and community)**:
The **partial match** is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via ChEBI, InChIKey, or enantiomer simplification). This step is optional, as it can be time-consuming depending on the number of unmatched entries.


Overview of the procedure
-------------------------

Pre-process mapping
~~~~~~~~~~~~~~~~~~~

For **metabolomic data**, whether provided as single or multiple files, metabolite information will be uniquely considered by a unique identifier such as ``unique-id``, ``common-name``, etc that is expected to be described in the first column of the input. Those identifiers will also be the unique values to which the output file relates to, indicating which metabolites were matched. Other columns, such as ``CHEBI``, ``INCHIKEY``, etc, available in the metabolite annotation tables will be considered as metadata to improve matching chances.

**Metabolic network data** is processed by extracting the identifiers and names of metabolites, together with all available metadata, such as ``ChEBI`` or ``InChIKey`` for instance.

Using the data above along with the ``conversion_datatable``, we test for matches as explained below.

Mapping procedure
~~~~~~~~~~~~~~~~~

- **Step 1: Match metabolomic data vs. metabolic network metadata**
  
  We first test for direct matches between metabolite information in metabolomic data and all the metadata in metabolic networks without going through the ``conversion_datatable`` table. 
  At the same time, for those that match, we verify whether they have a unique ID in ``conversion_datatable``.
  
- **Step 2: Match metabolomic data vs. conversion_datatable**
  
  Metabolites from metabolomics that did not match in the previous step will be tested here. Duplicate checks will be performed, since multiple columns from the metabolomic inputs will be tested for the same metabolite (i.e., within a single row). It is therefore possible that several identifiers of the conversion table match the same metabolite. In this case, the matches will be merged in the output table, separated by ``_AND_``. 
  For example, the UNIQUE-ID **CPD-17381** and the COMMON-NAME **roquefortine C** are identifiers that correspond to the same metabolite. In this case, it will be written as **CPD-17381 _AND_ roquefortine C**.

  Only matches are provided as outputs. Non-matching identifiers for a given metabolite will be excluded from MetaNetMap outputs to improve readability.


- **Step 3: Match metabolites in conversion_datatable vs. metabolic network metadata**
  
  This step continues the matching process for the metabolites that were mapped on the conversion datatable at Step 2, in order to associate them to metabolic network information, considering the additional identifiers that this knowledge base contains. Step 3 therefore search for matches against any metabolic network metadata.

  If none of the metabolic network identifiers match any conversion table reference, the information that a match with the conversion table occurred will still be provided in the output. If several distinct matches occurred, all of them will be merged in the result file (separated by ``_AND_``), as they represent the same metabolite. 
  This allows all information for one metabolite to be grouped on a single row, improving clarity and readability.

.. important::
    Regardless of whether partial match mode is disabled, the tool checks for potentially conflicting matches using only the unique identifier (e.g., the MetaCyc or MetaNetX UNIQUE-ID) to determine whether a metabolite from the input data corresponds to one or more metabolites in the reference database.
    When multiple input metabolites correspond to the same unique identifier, or vice versa, this situation is flagged as a partial match.

    The tool does not attempt to resolve this conflict automatically.
    Instead, these entries are explicitly marked, so the user can manually review and resolve the potential ambiguity. This ensures data integrity and allows the user to decide whether:
   - The match is correct and can be accepted;

   - The mapping should be adjusted or ignored;

   - Further curation is needed (e.g., manual verification against synonyms, names, or external identifiers).

    This behaviour helps avoid/reduce false positives during automatic matching.


Partial match (optional)
~~~~~~~~~~~~~~~~~~~~~~~~

When partial match mode is activated, the processing steps are first applied to the three knowledge tables (e.g., enantiomers, CHEBI). Afterward, all previous steps are repeated.

ChEBI/InChIKey processing is only performed if these identifiers are present in the metabolomic data table.

Once this processing is complete, the entire mapping pipeline is re-run, incorporating the modifications.

**The following treatments are applied:**

- **CHEBI** *(only if a CHEBI column exists in the metabolomics data)*:  
  For each row containing a ChEBI ID, the API of EBI is used to retrieve the full ChEBI ontology of the metabolite. These related terms are then remapped against the target databases.

- **INCHIKEY**:  
  An InChIKey is structured as `XXXXXXXXXXXXXX-YYYYYYYAB-Z`. The first block (`X`) represents the core molecular structure. We extract this primary structure to increase the chances of a match during the second mapping phase.

- **Enantiomers**:  
  Stereochemistry indicators (L, D, R, S) are removed from both the metabolomic data and the databases. This improves matching rates, since stereochemical information is often missing in metabolomic datasets.



License
-------

GNU Lesser General Public License v3 (LGPLv3)

Authors
-------

Coralie Muller, `Sylvain Prigent <https://bfp.bordeaux-aquitaine.hub.inrae.fr/personnel/pages-web-personnelles/prigent-sylvain>`__  and `Clémence Frioux <https://cfrioux.github.io>`__ -- `Inria Pleiade team <https://team.inria.fr/pleiade/>`__
