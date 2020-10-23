====================
Read a Blob File
====================

The second step is to read blob files from GC Image software.
In this case, it is much simpler because the files have always the same shape. Thus, a simple reader function is used.

.. code-block:: python

    import micropyro as mp

    blob_file = mp.read_blob_file('filename.cdf_img01_Blob_Table.csv')

We have some useful functions to, for example, check which compounds are not available in the database.
To do so, we need to pass the database dataframe and the blob file dataframe. The complete snippet looks as follows:

.. code-block:: python

    database = ReadDatabase.from_xls('Database_micropyro.xlsx')

    database_df = database.database

    blob_file = read_blob_file('241 ug Epoxy Py_600C-R_350C 105mL.cdf_img01_Blob_Table.csv')

    check_matches_database(database_df=database_df, blob_df=blob_file)

We can also access properties of a specific compound using pandas:

.. code-block:: python

    print(blob_file.volume["ethane"])

Description of the blob read file function is described here:

.. autofunction:: micropyro.read_blob_file


Matching blob file with database
--------------------------------

However, the most important part is to match the compounds in the blob file with the database,
thus grabbing the properties of interest from the database and passing them to the blob file. This is done using the
function :code:`perform_matching_database`:

.. code-block:: python

    perform_matching_database(blob_df=blob_file, database_df=database_df, extra_columns=['c'])

A description of this function is found below:

.. autofunction:: micropyro.perform_matching_database