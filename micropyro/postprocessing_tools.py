import textwrap

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm

def plot_n_highest_yields(blob_df, ncompounds, save_plot=None):
    """
    This utility plots the n compounds with the highest mrf yield.

    Parameters
    ----------
    blob_df: df
            Dataframe with the results
    ncompounds: int
            Number of compounds to be plotted
    save_plot: str
            Name of the output file
    """
    n_largest = blob_df.nlargest(ncompounds, 'yield mrf')

    ax = sns.barplot(x="index", y="yield mrf", data=n_largest.reset_index())

    max_width = 16
    ax.set_xticklabels(textwrap.fill(x.get_text(), max_width) for x in ax.get_xticklabels())

    ax.set(xlabel='compound', ylabel='yield mrf, \\%')

    # if you save in a file, I won't show it.
    if save_plot:
        ax.savefig(save_plot)
    else:
        plt.show()

def compare_yields(blob_dfs, compounds, x_axis = None, save_plot=None):
    """
    This utility compares the yields of different files (repetitions, temperatures, etc) .

    Parameters
    ----------
    blob_dfs: list of dfs
            List of Dataframes with the results
    compounds: list of strings
            Compounds to be plotted
    x_axis: list
            what to plot in the x axis, could be temperature, or whatever.
    save_plot: str
            Name of the output file

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """

    cmap = cm.get_cmap('tab10', 10)  # PiYG

    fig, ax = plt.subplots()

    for i_comp, compound in enumerate(compounds):
        color = cmap(i_comp)[:3]
        for i_df, df in enumerate(blob_dfs):

            yield_mrf = df.loc[compound].mrf
            ax.plot(x_axis[i_df], yield_mrf, 'o', color=color)

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax



