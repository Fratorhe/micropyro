==========================
Compute yields
==========================

The objective of this code is to actually compute the yields from the different compounds.
This can be done using different methods: using an internal standard, or *a-posteriori* calibration using one of the products.

Using Internal Standard (IS)
----------------------------

To do so, we use the function :code:`compute_yields_is`.
We need to pass the experimental matrix row and the blob file dataframes to the function, as well as the name of the IS.

.. code-block:: python

    compute_yields_is(experiment_df_row=experiment_df_row, blob_df=blob_file, internal_standard_name='fluoranthene')

This will add several columns to the blob_file dataframe. See below:

.. autofunction:: micropyro.compute_yields_is

To save the results, we export them to a csv file:

.. code-block:: python

    save_results_yields(blob_df, filename)

.. autofunction:: micropyro.save_results_yields


Internally, :code:`compute_yields_is` uses a support function to define the IS.
Normally, the user does not need to access it.

.. autofunction:: micropyro.define_internal_standard

