Overview
========
MetaNetMap aims to map metabolites between metabolomic data and metabolic networks.


.. image:: ./pictures/MetaNetMap_overview.png
   :alt: General overview of MetaNetMap
   :width: 80%


There are several challenges to this task:

- **ID homogenization in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools often assigns different IDs to the same metabolites. This inconsistency makes it difficult to cross-compare or transfer data across networks.

- **Metabolomic data complexities:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified as they are generally indistinguishable by standard LC–MS methods.

Successfully bridging metabolomic data and metabolic networks is complex but highly valuable, both for species-specific studies and community-level analyses.

Metanetmap enables this bridging process. We developed a tool that primarily allows the construction of a knowledge base, based on:

The ``datatable_conversion`` file acts as a bridge between the metabolomics data and the metabolic networks.  
It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``datatable_complementary`` file.  
This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  
By leveraging both the MetaCyc/MetaNetX database and user-provided enhancements, the ``datatable_conversion`` enables robust and flexible mapping across diverse data sources.


.. note::
   The test option is designed to work with the MetaCyc database.  
   However, information from MetaCyc related to the ontology of metabolites and pathways  
   is **not included** in the test option.  
   Only a simplified example (a "toy" version) of the ``datatable_conversion`` file is provided.

  But a conversion data table has already been built and is provided from MetaNetX in ``data/metanetx_conversion_datatable.tsv``.


After building this knowledge base - ``datatable_conversion``, it is possible to perform mapping in several ways

- **Classic mode**:
The classic mode allows you to input a single metabolomics data file and a directory containing multiple metabolic networks.

- **Community mode**:
The "community" mode allows you to input a directory containing multiple metabolomics data files, as well as a directory containing multiple metabolic networks.

- **Partial match (Option for mode classic and comminity)**:
The **partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).


More details in Application

License
-------

GNU Lesser General Public License v3 (LGPLv3)

Authors
-------

Coralie Muller, `Sylvain Prigent <https://bfp.bordeaux-aquitaine.hub.inrae.fr/personnel/pages-web-personnelles/prigent-sylvain>`__  and `Clémence Frioux <https://cfrioux.github.io>`__ -- `Inria Pleiade team <https://team.inria.fr/pleiade/>`__
