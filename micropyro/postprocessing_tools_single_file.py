import json
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

def get_yields_summary(blob_df, grouping, to_file=None):
    sum_groups = blob_df.groupby(grouping)['yield mrf'].sum()
    total = sum_groups.sum()
    sum_groups = sum_groups.to_dict()

    if to_file:
        dict_data = {**sum_groups, "total":total}
        with open(to_file, 'w') as fp:
            json.dump(dict_data, fp,indent=4)

    return sum_groups, total