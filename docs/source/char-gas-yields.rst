Gas and Char yields
=====================

In addition to the FID yields, we also have to include the gas and char yields to our mass balance.
Here there are some functions to make this easier. First, a generic reader for excel data based on
:meth:`micropyro.ReadExperimentTable`.
This function takes into account that any number reported in the tables can be
negative, thus if any is found, it will be set to 0.

.. autofunction:: micropyro.read_yields_excel


