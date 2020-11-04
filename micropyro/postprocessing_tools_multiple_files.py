import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm


def compare_yields(blob_dfs, compounds, x_axis=None, save_plot=None):
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
            try:
                yield_mrf = df.loc[compound, "yield mrf"]
                ax.plot(x_axis[i_df], yield_mrf, 'o', color=color)
            except KeyError:
                print(f'{compound} not found in {i_df}-th dataframe')

    for i_comp, compound in enumerate(compounds):
        ax.plot([], [], color=cmap(i_comp)[:3], linestyle='-', label=compound)

    ax.legend(loc='best')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax


def plot_ranges_MW(blob_dfs, ranges, x_axis=None, save_plot=None, filenames=None, plot_total=False):
    """
    This utility plots the yields based on ranges of MW.

    Parameters
    ----------
    blob_dfs: list of dfs
            List of Dataframes with the results
    ranges: list of floats
            Each number defines the upper bound for the range
    x_axis: list
            what to plot in the x axis, could be temperature, or whatever.
    save_plot: str
            Name of the output file
    plot_total: bool
            Plot the total yield
    filenames: list of strings or bool or None
            Plot the names of the files, or any other identifier of the samples.

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """
    ranges = [0] + ranges
    cmap = cm.get_cmap('tab10', 10)  # PiYG

    fig, ax = plt.subplots()

    for i_range, range_data in enumerate(ranges):
        # skip the first since it is forced to be 0
        if i_range == 0:
            continue
        color = cmap(i_range)[:3]
        for i_df, df in enumerate(blob_dfs):
            aux_df = df[(df.mw > ranges[i_range - 1]) & (df.mw < ranges[i_range])]
            yield_mrf = aux_df["yield mrf"].sum()
            ax.plot(x_axis[i_df], yield_mrf, 'o', color=color)

            if plot_total:
                ax.plot(x_axis[i_df], df["yield mrf"].sum(), 'o', color='k')

            # if provided plot the filenames, mostly for debugging
            if filenames:
                ax.annotate(filenames[i_df], (x_axis[i_df], yield_mrf))

    for i_range, range_data in enumerate(ranges):
        if i_range == 0:
            continue
        ax.plot([], [], color=cmap(i_range)[:3], linestyle='-', label=f'MW<{range_data}')

    if plot_total:
        ax.plot([], [], color='k', linestyle='-', label=f'Total')

    ax.legend(loc='best')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax


def compare_quantites_totals(list_totals_dict, quantity, subgroups=None, x_axis=None, save_plot=None):
    """
    This utility compares the a given quantity from the total files for different files (repetitions, temperatures, etc).

    Parameters
    ----------
    list_totals_dict: list of dfs
            List of dicts with the totals.
    quantity: str
            Quantity to compare (atoms, total, grouping, etc)
    subgroup: list of str
            subgroup to plot (if quantity is atoms, subgroup will be c, h, o, n.)
            if not provided, it will try to guess it.
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

    if not subgroups:
        subgroups = list_totals_dict[0][quantity].keys() # if subgroup not given, guess it from the first file.


    fig, ax = plt.subplots()

    for i_group, group in enumerate(subgroups):
        color = cmap(i_group)[:3]
        for i_dict_totals, dict_totals in enumerate(list_totals_dict):
            try:
                quantity_group = dict_totals[quantity][group]
                ax.plot(x_axis[i_dict_totals], quantity_group, 'o', color=color)
            except KeyError:
                print(f'{group} not found in {i_dict_totals}-th dictionary')

    for i_group, group in enumerate(subgroups):
        ax.plot([], [], color=cmap(i_group)[:3], linestyle='-', label=group)

    ax.legend(loc='best')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax

def compare_elements_totals(list_totals_dict, elements=['c','o','h','n'], x_axis=None, save_plot=None):
    """
        This utility compares the elements for given results files (repetitions, temperatures, etc).
        Basically particularizes compare_quantites_totals

        Parameters
        ----------
        list_totals_dict: list of dfs
                List of dicts with the totals.
        elements: list of str
                list of atoms to plot, if not provided, use the list by default
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
    fig, ax = compare_quantites_totals(list_totals_dict, 'atoms', elements, x_axis, save_plot=False)
    ax.set_ylabel('Mass Yield, \\%')
    ax.set_xlabel('Temperature, C')

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax

def compare_group_totals(list_totals_dict, group_name, x_axis=None, save_plot=None):
    """
        This utility compares the groups for given results files (repetitions, temperatures, etc).
        Basically particularizes compare_quantites_totals

        Parameters
        ----------
        list_totals_dict: list of dfs
                List of dicts with the totals.
        elements: list of str
                list of atoms to plot, if not provided, use the list by default
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
    fig, ax = compare_quantites_totals(list_totals_dict, quantity=group_name, x_axis=x_axis, save_plot=False)
    ax.set_ylabel('Mass Yield, \\%')
    ax.set_xlabel('Temperature, C')

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax