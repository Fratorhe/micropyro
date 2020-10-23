==================
Generate Database
==================

We can also generate the database automatically, with only the compound names. However, this requires several chemistry
libraries which are somewhat difficult to install/setup...So far, I only managed to make it work on Linux.

Requirements
--------------
It is required to compile from sources the code `OpenBabel <https://github.com/openbabel/openbabel>`_. To do so, do
the following (may require sudo):

.. code-block:: shell-session

    $ git clone https://github.com/openbabel/openbabel
    $ cd openbabel
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make -j8
    $ make install

Once this is done, install the following packages, for Ubuntu:

.. code-block:: shell-session

    $ sudo apt-get install python python-setuptools python-dev python-augeas gcc swig dialog

Finally, install the python wrapper:

.. code-block:: shell-session

    $ pip install openbabel

If this gives an error, download the package from PyPI, and install it manually.

We also need the python package for PubChem, this one is much easier:

.. code-block:: shell-session

    $ pip install pubchempy

Usage
--------------

Once this is done, creating the database is easy:

.. code-block:: python

    import micropyro as mp

    database = mp.GenerateDatabase.from_csv('database_example.csv')
    database.get_formula_mw()
    database.get_benzene_rings()
    database.to_csv()

The database to be generated requires a column with the header **Compound** and the different compounds below.

.. autoclass:: micropyro.GenerateDatabase

