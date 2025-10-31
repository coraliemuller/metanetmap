

[![PyPI version](https://img.shields.io/pypi/v/metanetmap.svg)](https://pypi.org/project/metanetmap/) [![GitHub license](https://img.shields.io/github/license/coraliemuller/metanetmap.svg)](https://github.com/coraliemuller/metanetmap/blob/main/LICENSE) [![Actions Status](https://github.com/coraliemuller/metanetmap/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/coraliemuller/metanetmap/actions/workflows/pythonpackage.yml) [![Documentation Status](https://readthedocs.org/projects/metanetmap/badge/?version=latest)](https://metanetmap.readthedocs.io/en/latest/?badge=latest)

# Metabolomic data - metabolic Network Mapping (MetaNetMap)

[MetaNetMap](https://github.com/coraliemuller/metanetmap) aims at map metabolites between metabolomic data and metabolic networks.
The goal is to facilitate the identification of metabolites from **metabolomics data** that are also present in one or more **metabolic networks**.

This approach makes it possible to distinguish between metabolites that are easily identifiable through well-known identifiers and those that are more difficult to annotate or identify within metabolic networks.


<div align="center">
  <img src="/docs/pictures/MetaNetMap_overview.png" alt="General overview of MetaNetMap" width="100%">
</div>


There are several challenges to this task:

- **ID homogenization in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools often assigns different IDs to the same metabolites. This inconsistency makes it difficult to cross-compare or transfer data across networks.

- **Metabolomic data complexities:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified because they are indistinguishable by LC/MS methods.

Successfully bridging metabolomic data and metabolic networks is complex but highly valuable, both for species-specific studies and community-level analyses.

Metanetmap enables this bridging process. We developed a tool that primarily allows the construction of a knowledge base, based on:

The ``datatable_conversion`` file acts as a bridge between the metabolomics data and the metabolic networks.  
It combines all structured information extracted from the MetaCyc ``compounds.dat`` file or from MetaNetX files ``chem_xref.tsv`` and ``chem_prop.tsv``files, along with any additional identifiers or metadata provided by the user through the ``datatable_complementary`` file.  
This unified table serves as a comprehensive knowledge base that allows the tool to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  
By leveraging both the MetaCyc/MetaNetX database and user-provided enhancements, the ``datatable_conversion`` enables robust and flexible mapping across diverse data sources.

A conversion data table has already been built and is provided from MetaNetX in ``data/metanetx_conversion_datatable.tsv``.


## Installation

The application is tested on Python versions 3.11 Ubuntu.

Install with pip:

```sh
pip install metanetmap
```

Or from source:

```sh
git clone git@gitlab.inria.fr:mistic/metanetmap.git
cd metanetmap
pip install -r requirements.txt
pip install -r requirements_dev.txt
pip install .
```

## Quickstart

To test the tool with toys data:

Two modes are available for testing, with an option to enable or disable **partial match**.

The **Partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).


### Classic mode
The classic mode allows you to input a single metabolomics data file (.maf) and a directory containing multiple metabolic networks (.sbml/.xml).

```bash
metanetmap test
```

#### Classic mode with partial match activated
```bash
metanetmap test --partial_match
```

### Community mode
The "community" mode allows you to input a directory containing multiple metabolomics data files (.maf), as well as a directory containing multiple metabolic networks(.sbml/.xml).

```bash
metanetmap test --community
```

#### Community mode with partial match activated
```bash
metanetmap test --community --partial_match
```


> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/info.svg">
>   <img alt="Info" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/info.svg">
> </picture><br>
> Metacyc database information related to the ontology of metabolites and pathways is not included in test option.


> :warning:  We assume that you arrive at this step having installed the tool first (see above), for instance in a Python virtual environment, or conda (mamba) environment.


For full documentation, usage, and advanced options, see the [online documentation](https://MetaNetMap.readthedocs.io/).

## License

GNU Lesser General Public License v3 (LGPLv3)

## Authors

Coralie Muller, [Sylvain Prigent](https://bfp.bordeaux-aquitaine.hub.inrae.fr/personnel/pages-web-personnelles/prigent-sylvain) and  [Clémence Frioux](https://cfrioux.github.io) 