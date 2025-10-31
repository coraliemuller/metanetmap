.. highlight:: shell

============
Installation
============


Stable release
--------------

To install MetaNetMap, run this command in your terminal:

At the command line:

  .. code-block:: bash
        pip install metanetmap

To install the latest development version from source:

  .. code-block:: bash
        git clone git@gitlab.inria.fr:mistic/metanetmap.git
        cd metanetmap
        pip install -r requirements.txt
        pip install -r requirements_dev.txt
        pip install .

Dependencies
============

MetaNetMap dependencies:

- pandas
- numpy
- cobra
- setuptools
- aiohttp
- tqdm


See Quickstart in the :doc:`quickstart`.
