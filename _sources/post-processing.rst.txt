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