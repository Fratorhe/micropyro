====================
Post processing
====================

Here, we show several tools to perform postprocessing on the yield data.
To read the results file(s), we can use the reader :meth:`micropyro.read_blob_file`.


Single file tools
------------------

Plots
^^^^^^^

We can plot the *n* compounds with highest yield. We use the function :meth:`micropyro.plot_n_highest_yields`:

.. autofunction:: micropyro.plot_n_highest_yields

As example, we can do:

.. code-block:: python

    import micropyro as mp
    results_df = mp.read_blob_file("100 ug Py_600C.results.csv", index_col=0)
    mp.plot_n_highest_yields(results_df, 5)


Yields
^^^^^^^

You may also be interested on computing the yields based on the elements.
Remember to add the appropriate elements to the columns in :meth:`perform_matching_database`
To compute the elemental composition, simply run the following:

.. code-block:: python

    results_df = mp.read_blob_file("241 ug Py_850C.results.csv", index_col=0)
    data_per_atom = mp.compute_elemental_composition(results_df)
    print(data_per_atom)

.. autofunction:: micropyro.compute_elemental_composition

The yields can be analyzed using groupings. To add new groupings, add it as new columns in the database,
and remember to include those extra columns in :meth:`perform_matching_database`.
In a single line, this can be analyzed.
This summary will also perform the elemental composition computation shown above, unless specified otherwise.
If specified, results are exported to json for further processing.

.. code-block:: python

    data_yields = mp.get_yields_summary(results_df, "grouping", to_file='100 ug Py_600C.totals.csv')
    print(f'The different groups are: {data_yields["grouping"]}')
    print(f'The total FID yield is: {data_yields["total"]}')
    print(f'The per-atom yield is: {data_yields["atoms"]}')

.. autofunction:: micropyro.get_yields_summary

Multiple files tools
---------------------

We can process several files at the same time to study trends, etc.
A utility :meth:`micropyro.compare_yields` can be used.

.. autofunction:: micropyro.compare_yields

As example, we can do:

.. code-block:: python

    import micropyro as mp
    results_df1 = mp.read_blob_file("241 ug Py_850C.results.csv", index_col=0)
    results_df2 = mp.read_blob_file("100 ug Py_600C.results.csv", index_col=0)
    fig, ax = mp.compare_yields([results_df1, results_df2], compounds=['phenol', 'methane'],
                                save_plot='comparison.pdf', x_axis = [350, 300])
    ax.set_xlabel('2nd Reactor Temperature, C')
    ax.set_ylabel('Yield, %')
    plt.show()