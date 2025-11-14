

[![PyPI version](https://img.shields.io/pypi/v/metanetmap.svg)](https://pypi.org/project/metanetmap/) [![GitHub license](https://img.shields.io/github/license/coraliemuller/metanetmap.svg)](https://github.com/coraliemuller/metanetmap/blob/main/LICENSE) [![Actions Status](https://github.com/coraliemuller/metanetmap/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/coraliemuller/metanetmap/actions/workflows/pythonpackage.yml) [![Documentation Status](https://readthedocs.org/projects/metanetmap/badge/?version=latest)](https://metanetmap.readthedocs.io/en/latest/?badge=latest)

# Metabolomic data - metabolic Network Mapping (MetaNetMap)

[MetaNetMap](https://github.com/coraliemuller/metanetmap) is a Python tool dedicated to mapping metabolite information between metabolomic data and metabolic networks.
The goal is to facilitate the identification of metabolites from **metabolomics data** that are also present in one or more **metabolic networks**, taking into consideration that data from the former has distinct identifier from the latter.

Some metabolites can be rather easily identifiable using intermediate well-known identifiers, whereas for others, mapping is more difficult and may require partial matching. The picture below summarises the mapping procedure implemented in MetaNetMap. 

For full documentation, usage, and advanced options, see the [online documentation](https://MetaNetMap.readthedocs.io/).


<div align="center">
  <img src="docs/pictures/MetaNetMap_overview.png" alt="General overview of MetaNetMap" width="100%">
</div>

## Why using this tool to map metabolomic data?

- **ID variability in metabolic networks:**  
  Automatic reconstruction of metabolic networks using different tools often assigns different IDs to the same metabolites. It is likely that those do not match the nomenclature of metabolomic annotations. To reconcile them, metadata from metabolic networks associating molecules to alternative databases can be used, so can third-party external databases such as [https://www.metanetx.org](MetaNetX). MetaNetMap provides such functionalities. 

- **Metabolomic data complexity:**  
  Due to the difficulty of annotating metabolomic profiles, identifications are often partial, incomplete, and inconsistently represented. For example, enantiomers are frequently not precisely specified because they are indistinguishable by LC/MS methods. Matching must account for this.

MetaNetMap can match one or several metabolomic annotation tables to one or several metabolic networks. 

### Third-party database for matching

In case metadata from metabolic network do not match identifiers of the metabolomic data, a third-party database, referred to as *conversion_datatable* file acts as a bridge between the metabolomics data and the metabolic networks.  

MetaNetMap enables the construction of such resource using MetaNetX or MetaCyc knowledge bases. In the former case, data from ``chem_xref.tsv`` and ``chem_prop.tsv`` MetaNetX files is used. In the latter case (requires a licence), metadata from the ``compounds.dat`` file is extracted. Additionally, users can provide another table with existing mapping data, referred to as *datatable_complementary*.
  
The resulting table serves as a comprehensive knowledge base that allows MetaNetMap to search across all known identifiers for a given metabolite and match them between the input data and the metabolic networks.  

Refer to the documentation to build your first mapping table, using MetaNetX data.

## Installation

The application is tested with Python v.3.11 on Ubuntu, MacOS and Windows.

Install with pip:

```sh
pip install metanetmap
```

Or from source:

```sh
git clone git@github.com:coraliemuller/metanetmap.git
cd metanetmap
pip install -r requirements.txt
pip install .
```

To install the latest development version from source :

```sh
git clone git@github.com:coraliemuller/metanetmap.git
cd metanetmap
pip install -r requirements.txt
pip install -r requirements_dev.txt
pip install .
```

## Quickstart

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/info.svg">
>   <img alt="Info" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/info.svg">
> </picture><br>
> We assume that you arrive at this step having installed the tool first (see above), for instance in a Python virtual environment, or conda (mamba) environment.


To test the tool with toy data:

Two modes are available for testing, with an option to enable or disable **partial match**.

The **Partial match** is optional, as it can be time-consuming. It is a post-processing step applied to metabolites or IDs that were not successfully mapped during the initial run. These unmatched entries are re-evaluated using specific strategies, which increase the chances of finding a match (e.g., via CHEBI, INCHIKEY, or enantiomer simplification).


### Classic mode
The classic mode allows you to input a single metabolomics data file (`.maf` or `.tsv`) or a directory containing multiple metabolomics data files, and a unique metabolic network (`.sbml` or `.xml`).

```bash
metanetmap test
```

#### Classic mode with partial match activated
```bash
metanetmap test --partial_match
```

### Community mode
The "community" mode allows you to input a directory containing multiple metabolomic data files (`.maf` or `.tsv`), as well as a directory containing multiple metabolic networks(`.sbml` or `.xml`).

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
>

For full documentation, usage, and advanced options, see the [online documentation](https://MetaNetMap.readthedocs.io/).


## Citations

If you use MetaNetMap, please cite:

- Muller, C. et al (2025). MetaNetMap: automatic mapping of metabolomic
data onto metabolic networks. BioRxiv.
  
If you use the default MetaNetX third-party database, please cite additionally:

- Moretti, S., Tran, V. D. T., Mehl, F., Ibberson, M., and Pagni, M. (2020). MetaNetX/MNXref: unified namespace for metabolites and biochemical reactions in the context of metabolic models. Nucleic Acids Research, 49(D1), gkaa992-. [https://doi.org/10.1093/nar/gkaa992](https://doi.org/10.1093/nar/gkaa992)


## License

GNU Lesser General Public License v3 (LGPLv3)

## Authors

Coralie Muller, [Sylvain Prigent](https://bfp.bordeaux-aquitaine.hub.inrae.fr/personnel/pages-web-personnelles/prigent-sylvain) and  [Clémence Frioux](https://cfrioux.github.io) 