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

Internally, :code:`compute_yields_is` uses a support function to define the IS.
Normally, the user does not need to access it.

.. autofunction:: micropyro.define_internal_standard

Using a reference compound
----------------------------

To do so, we use the function :code:`compute_yields_calib`. It is actually quite similar to the previous.
However, in this case, we pass the experimental matrix row and the blob file dataframes to the function,
the name of the calibration file, the reference compound for which calibration was done,
and if any compound needs to be dropped from the blob dataframe. The possibility of dropping is due to the fact
that sometimes we use also the IS, and we do not want it in the yields computation.

.. code-block:: python

    compute_yields_calibration(experiment_df_row=experiment_df_row, blob_df=blob_file, calibration_file='phenol_calibration.json',
                           compound_drop='fluoranthene', reference_compound='phenol')

This will add several columns to the blob_file dataframe. See below:

.. autofunction:: micropyro.compute_yields_calibration

To save the results, we export them to a csv file:

.. code-block:: python

    save_results_yields(blob_df, filename)

Internally, :code:`compute_yields_is` uses a support function to compute the mass from the calibration curve.
Normally, the user does not need to access it.

.. autofunction:: micropyro.get_mass_calibration


Internal logic
----------------------------

Both IS method and linear calibration use the same function to compute. In the first, the mass of IS is obtained
directly, while in the second it is computed through the calibration file.
A description of the actual function doing the job is found below:

.. autofunction:: micropyro.compute_yields

To save the results, we also use the same function:

.. autofunction:: micropyro.save_results_yields