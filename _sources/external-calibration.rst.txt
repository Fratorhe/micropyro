=======================
External calibration
=======================

Performing the external calibration is rather a simple task.
Typically, a linear regression model is used forcing to cross the origin.

A class :code:`ExternalCalibration` has been implemented to make this task easy.
As with other classes, one may use several constructors since data can be in different formats.
So far, only excel and native dataframe are supported. Outliers and missing data are removed automatically.

To perform a calibration, we need only 3 lines of code:

.. code-block:: python

    import micropyro as mp
    calibration = mp.ExternalCalibration.from_xls(file_to_read, sheet_name="Phenol", skiprows=1, header=0,
                                           usecols="A:J")
    calibration.linear_calibration(to_file="phenol_calibration.json")
    calibration.plot_calibration(save_plot='phenol.pdf')

A detailed implementation of the class:

.. autoclass:: micropyro.ExternalCalibration
    :members: linear_calibration



