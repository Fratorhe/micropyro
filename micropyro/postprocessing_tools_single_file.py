import json
import textwrap

import matplotlib.pyplot as plt
import pkg_resources
import seaborn as sns

import micropyro as mp


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

    max_width = 12
    ax.set_xticklabels(textwrap.fill(x.get_text(), max_width) for x in ax.get_xticklabels())
    plt.setp(ax.get_xticklabels(), fontsize=15)
    ax.set(xlabel='compound', ylabel='yield mrf, \\%')

    # if you save in a file, I won't show it.
    if save_plot:
        plt.savefig(save_plot)

    return ax

def get_yields_summary(blob_df, grouping=None, to_file=None):
    """
    This utility computes the yields for the atoms based on the grouping.
    In addition provides the total FID yield, and the yield per atom if requested.
    Sum of elemental and total may slightly differ due to isotopes.

    Parameters
    ----------
    blob_df: df
            Dataframe with the results
    grouping: str
            Name of the grouping to be used
    to_file: str
            Name of the output file

    Returns
    ---------
    dict_data: dict
            Dictionary with the grouping, the total and the elemental composition.
    """

    if grouping:
        sum_groups = blob_df.groupby(grouping)['yield mrf'].sum()
    else:
        sum_groups = {}

    total = blob_df['yield mrf'].sum()
    sum_groups = sum_groups.to_dict()

    dict_per_atom = compute_elemental_composition(blob_df)

    dict_data = {grouping: sum_groups, "total_FID": total, "atoms_FID": dict_per_atom}
    if to_file:
        with open(to_file, 'w') as fp:
            json.dump(dict_data, fp, indent=4)

    return dict_data


def compute_elemental_composition(blob_df):
    """
    This function computes the elemental compositon per atom of the blob_df.
    To do so, of course, you will have to add the extra columns to the df when performing the database matching.

    Parameters
    -----------
    blob_df: df
        dataframe with results

    Returns
    -----------
    data_per_atom: dict
        dictionary with mass yield per atom for the given blob_df
    """

    # gets the atoms from the database
    data_atoms = mp.get_atom_mw_dict()
    data_per_atom = {}

    for atom in data_atoms.keys():
        try:
            MW_atom = data_atoms[atom]["mw"]
            blob_df[f'%{atom}'] = blob_df.apply(lambda row: row["yield mrf"] / float(row["mw"]) * float(row[atom]) * MW_atom, axis=1)
            data_per_atom[atom] = blob_df[f'%{atom}'].sum()
        except KeyError:
            print(f"Compounds with {atom.upper()} not found.")
            pass

    return data_per_atom
