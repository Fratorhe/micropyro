=====
Usage
=====

Start by importing micropyro (use abbreviation :code:`mp` to look fancy).

.. code-block:: python

    import micropyro as mp


Read a Database
----------------
Reading a database is usually the first task to be done when computing yields.
This is done using the class :code:`ReadDatabase`
If you are importing it from an excel file:

.. code-block:: python

    import micropyro as mp

    db = mp.ReadDatabase.from_xls('Database_micropyro.xlsx')

This internally computes also the number of atoms from each atom type, and the ECN and MRF for each compound.
The actual database can be accessed by the attribute :code:`database`.asdf
Specific compound or columns can be accessed as follows:

.. code-block:: python

    print(db.database)
    print(db.database.c["ethane"])
    print(db.database.formula["ethane"])
    print(db.database.grouping["ethane"])
    print(db.database.mrf)

A description of the class is found here:

.. autoclass:: micropyro.read_database.ReadDatabase