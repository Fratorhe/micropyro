import matplotlib.pyplot as plt
import numpy as np
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
        ax.plot([], [], color=cmap(i_range)[:3], linestyle='-', label=f'{ranges[i_range - 1]}$<$MW$<${range_data}')

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
        subgroups = list_totals_dict[0][quantity].keys()  # if subgroup not given, guess it from the first file.

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


def compare_elements_totals(list_totals_dict, elements=['c', 'o', 'h', 'n'], x_axis=None, save_plot=None):
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


def plot_total_globals(list_totals_dict, x_axis=None, save_plot=None, annotate=False):
    """
    Function to wrap compare_group_totals to only plot the global totals (char, gas and FID)

    Parameters
    ----------
    list_totals_dict: list of dfs
        List of dicts with the totals.

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """

    fig, ax = plt.subplots()

    yield_names = ('char_yield', 'total_FID', 'total_gases')
    dict_totals_plot = {'char_yield': [], 'total_FID': [], 'total_gases': [], 'total_sum': []}
    annotations = []

    for dict_totals in list_totals_dict:
        yields = []  # container to add the yields of a single measurement (gas, char, fid)
        for yield_to_add in yield_names:
            extracted_yield_from_json = dict_totals.get(yield_to_add, np.nan)  # get it from the json file
            yields.append(extracted_yield_from_json)  # add it to the container
            dict_totals_plot[yield_to_add].append(extracted_yield_from_json)  # add it to the dictionary

        total = np.nansum(yields)  # adds all of them considering nans = 0
        dict_totals_plot['total_sum'].append(total)
        if annotate:
            mass = f'{dict_totals["mass ug"]:.0f} ug' if not np.isnan(dict_totals["mass ug"]) else ''
            first_react = f'{dict_totals["1st_react_temp"]:.0f} C' if not np.isnan(dict_totals["1st_react_temp"]) else ''
            second_react = f'{dict_totals["2nd_react_temp"]:.0f} C' if not np.isnan(dict_totals["2nd_react_temp"]) else ''
            annotations.append(f'{mass} {first_react} {second_react}')

    conversion_names_label = {'char_yield': 'Char', 'total_FID': 'FID',
                              'total_gases': 'Light Gases', 'total_sum': 'Total'}

    if x_axis is None:
        # x axis will be set to the temperature of the first reactor
        x_axis = []
        for dict_totals in list_totals_dict:
            x_axis.append(dict_totals['1st_react_temp'])

    for quantity_plot, values_plot in dict_totals_plot.items():
        ax.scatter(x_axis, values_plot, label=conversion_names_label[quantity_plot])

    if annotate:
        for _, values_plot in dict_totals_plot.items():  # this iterates over char, gas, fid and total.
            # this iterates over a temperatures, and one of the above getting a pair (T, yield)
            for x_axis_value, value_plot, annotation in zip(x_axis, values_plot,annotations):
                ax.annotate(annotation, (x_axis_value, value_plot), fontsize=16, alpha=0.5)

    ax.legend(loc='best')
    ax.set_ylabel('Mass Yield, \\%')
    ax.set_xlabel('Temperature, C')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax
