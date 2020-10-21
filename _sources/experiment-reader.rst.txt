==========================
Read experimental matrix
==========================

Typically, one performs several experiments and keeps track of them in a more or less simple excel sheet.
Usually, one records the mass of the different components, including sample and internal standard, etc.
The filename is also recorded and used as index in the following as it is a good (unique) identifier.
A class :code:`ReadExperimentTable` is used to read the experimental matrix.
As with the database, several types of files may be used for this, but for the moment, let us focus on xls files.
Then, the experimental matrix can be read:

.. code-block:: python

    import micropyro as mp

    exp_matrix = mp.ReadExperimentTable.from_xls("Micropyrolysis.xlsx",
                                          sheet_name="Micropyro", skiprows=1, header=0,
                                          usecols="A:V")

In this case, we skip the first row (skiprows=1), we set the first read column as the header, and then use only columns from A to V.

Often, we use internal standard mixture, but we are interested only in the part that gets pyrolyzed, thus its contribution can be obtained using:

.. code-block:: python

    exp_matrix.compute_is_amount(concentration=0.0335)

We can also compute the char content, given the mass before and after:

.. code-block:: python

    exp_matrix.compute_char()

A specific row can be extracted using pandas syntax:

.. code-block:: python

    experiment_df_row = exp_matrix.experiment_df.loc["100 ug material py_600c"]

But we can access any quantity, anytime. To plot the char yield, we simply:

.. code-block:: python

    import matplotlib.pyplot as plt # required for plotting

    char_yield = exp_matrix.experiment_df["% char"]
    temperature = exp_matrix.experiment_df.temperature
    plt.plot(temperature, char_yield, "o")
    plt.savefig("char_yield.pdf")  # save it to a file

The description of the class is as follows:

.. autoclass:: micropyro.ReadExperimentTable

