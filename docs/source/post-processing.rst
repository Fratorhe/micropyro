====================
Post processing
====================

Here, we show several tools to perform postprocessing on the yield data.
To read the results file(s), we can use the reader :meth:`micropyro.read_blob_file`.


Single file tools
------------------

We can plot the *n* compounds with highest yield. We use the function :meth:`micropyro.plot_n_highest_yields`:

.. autofunction:: micropyro.plot_n_highest_yields

As example, we can do:

.. code-block:: python

    import micropyro as mp
    results_df = mp.read_blob_file("100 ug Py_600C.results.csv", index_col=0)
    mp.plot_n_highest_yields(results_df, 5)

The yields can be analyzed using groupings. To add new groupings, add it as new columns in the database,
and remember to include those extra columns in :meth:`perform_matching_database`.
In a single line, this can be analyzed. If specified, results are exported to json for further processing.

.. code-block:: python

    sum_groups, total = mp.get_yields_summary(results_df, "grouping", to_file='100 ug Py_600C.totals.csv')
    print(f'The different groups are: {sum_groups}')
    print(f'The total FID yield is: {total}')

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