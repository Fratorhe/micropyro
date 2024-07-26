import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from scipy.interpolate import interpolate, interp1d
from scipy.signal import savgol_filter

from micropyro import get_markers, get_linestyles

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


def plot_ranges_MW(blob_dfs, ranges, x_axis=None, save_plot=None, lines=True,
                   plot_total=False, ax=None, fig=None, legend=True, errorbarvalue=None, **kwargs):
    """
    This utility plots the yields based on ranges of MW.

    Parameters
    ----------
    blob_dfs: list of dfs
            List of Dataframes with the results
    ranges: list of floats
            Each pair of numbers define the range
    x_axis: list
            what to plot in the x axis, could be temperature, or whatever.
    save_plot: str
            Name of the output file
    plot_total: bool
            Plot the total yield
    filenames: list of strings or bool or None
            Plot the names of the files, or any other identifier of the samples.
    errorbarvalue: % of errorbar wrt to the nominal value. typically 1sigma

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """

    cmap = cm.get_cmap('tab10', 10)  # PiYG
    plt.gca().set_prop_cycle(None)

    if not ax:
        fig, ax = plt.subplots()

    markers = get_markers()
    if lines:
        linestyle = get_linestyles()
    else:
        linestyle = len(ranges)*[""]

    dict_ranges_data = {k: [] for k in ranges[1:]}

    for i_range, range_data in enumerate(ranges):
        # skip the first since it is forced to be 0
        if i_range == 0:
            continue
        for i_df, df in enumerate(blob_dfs):
            aux_df = df[(df.mw > ranges[i_range - 1]) & (df.mw < ranges[i_range])]
            yield_mrf = aux_df["yield mrf"].sum()
            dict_ranges_data[range_data].append(yield_mrf)

    for i_range, range_data in enumerate(dict_ranges_data.keys()):
        if legend:
            label = f'{ranges[i_range]}$<$MW$<${range_data}'
        else:
            label = None

        # if errorbars, compute the values, and add them.
        if errorbarvalue:
            errors = np.array(dict_ranges_data[range_data]) * errorbarvalue / 100
            ax.errorbar(x_axis, dict_ranges_data[range_data],yerr=errors, fmt='o', color=cmap(i_range + 1)[:3],
                    label=label, marker=markers[i_range], linestyle=linestyle[i_range], **kwargs)
        else:
            ax.plot(x_axis, dict_ranges_data[range_data], 'o', color=cmap(i_range + 1)[:3],
                    label=label, marker=markers[i_range], linestyle=linestyle[i_range], **kwargs)

    if plot_total:
        ax.plot([], [], color=cmap(i_range + 1)[:3], linestyle='-', label=f'Total', **kwargs)

    if legend:
        ax.legend(loc='best')

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax


def compare_quantites_totals(list_totals_dict, quantity, subgroups=None, x_axis=None, save_plot=None, ax=None, fig=None,
                             legend=True, ordered=False, errorbar=False, **kwargs):
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
    markers = get_markers()

    start = 0
    if 'start' in kwargs:
        start = kwargs['start']
        kwargs.pop('start', None)

    if not ax:
        fig, ax = plt.subplots()

    if not subgroups:
        subgroups = list_totals_dict[0][quantity].keys()  # if subgroup not given, guess it from the first file.

    # TODO: refurbish this: first get the data, then plot it after. like this we can implement cumulative if needed.
    for i_group, group in enumerate(subgroups, start=start):
        color = cmap(i_group)[:3]
        data_plot = []
        for i_dict_totals, dict_totals in enumerate(list_totals_dict):
            quantity_group = dict_totals[quantity].get(group,0)
            data_plot.append(quantity_group)

        if ordered:
            x_axis_plot, data_plot = zip(*sorted(zip(x_axis, data_plot)))
        else:
            x_axis_plot = x_axis



        if errorbar:
            errors = np.array(data_plot) * errorbar / 100
            ax.errorbar(x_axis_plot, data_plot, yerr=errors, marker=markers[i_group], color=color, linewidth=1,
                        capsize=10,linestyle="None", **kwargs)
        else:
            ax.plot(x_axis_plot, data_plot, '--',marker=markers[i_group], color=color, **kwargs, linewidth=1)

        try:
            x_axis_plot_smooth = np.linspace(x_axis_plot[0], x_axis_plot[-1], 100)
            a_BSpline = interp1d(x_axis_plot, data_plot, kind='quadratic')
            data_plot_smooth = savgol_filter(a_BSpline(x_axis_plot_smooth), 65, 3)
            ax.plot(x_axis_plot_smooth, data_plot_smooth, '--', color=color, linewidth=1, alpha=0.7,**kwargs)
        except:
            pass

    if legend:
        for i_group, group in enumerate(subgroups, start=start):
            if len(group) == 1:
                group = group.upper()  # basically if it's an element
            if errorbar:
                ax.errorbar([], [], yerr=1, color=cmap(i_group)[:3], linestyle='--', label=group, marker=markers[i_group])
            else:
                ax.plot([], [], color=cmap(i_group)[:3], linestyle='-', label=group)

    ax.legend(loc='best',prop={'size': 25})
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
    fig, ax = compare_quantites_totals(list_totals_dict, 'atoms_FID', elements, x_axis, save_plot=False)
    ax.set_ylabel('Mass Yield, \\%')
    ax.set_xlabel('Temperature, \N{DEGREE SIGN}C')

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax


def compare_group_totals(list_totals_dict, group_name, x_axis=None, save_plot=None, ordered=False, fig=None, ax=None, errorbar=False, **kwargs):
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
    fig, ax = compare_quantites_totals(list_totals_dict, quantity=group_name, x_axis=x_axis, ordered=ordered, fig=fig, ax=ax, errorbar=errorbar, **kwargs)
    ax.set_ylabel('Yield, wt.\\%')
    ax.set_xlabel('Temperature, \N{DEGREE SIGN}C')

    if save_plot:
        fig.savefig(save_plot)

    return fig, ax


def plot_total_globals(list_totals_dict, x_axis=None, save_plot=None, annotate=False,
                       errorbars=None, ax=None, fig=None, legend=True, **kwargs):
    """
    Function to wrap compare_group_totals to only plot the global totals (char, gas and FID)

    Parameters
    ----------
    list_totals_dict: list of dfs
        List of dicts with the totals.
    annotate: bool
        annotates the filenames
    save_plot: bool or str
        Save to a file with this name
    x_axis: None or 1D array
        to be used as x axis, if not given will use temperature of 1st reactor
    errorbars: None, False or dict
        If none or false, nothing shows. If a dict, will use it as % of the plotted quantities to create errorbars

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """
    plt.gca().set_prop_cycle(None)

    markers = get_markers()

    if ax is None:
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
            first_react = f'{dict_totals["1st_react_temp"]:.0f} C' if not np.isnan(
                dict_totals["1st_react_temp"]) else ''
            second_react = f'{dict_totals["2nd_react_temp"]:.0f} C' if not np.isnan(
                dict_totals["2nd_react_temp"]) else ''
            annotations.append(f'{mass} {first_react} {second_react}')

    conversion_names_label = {'char_yield': 'Char', 'total_FID': 'Vapors within GC range',
                              'total_gases': 'Light Gases', 'total_sum': 'Total'}

    if x_axis is None:
        # x axis will be set to the temperature of the first reactor
        x_axis = []
        for dict_totals in list_totals_dict:
            x_axis.append(dict_totals['1st_react_temp'])

    if not errorbars:
        for idx, (quantity_plot, values_plot) in enumerate(dict_totals_plot.items()):
            ax.scatter(x_axis, values_plot, label=conversion_names_label[quantity_plot], marker=markers[idx], **kwargs)

    if errorbars:
        error_total = []
        for idx, (quantity_plot, values_plot) in enumerate(dict_totals_plot.items()):
            errors = np.array(values_plot) * errorbars[quantity_plot] / 100
            if quantity_plot == 'total_sum':
                errors = np.sqrt(np.sum(np.square(error_total), axis=0))
            ax.errorbar(x_axis, values_plot, yerr=errors, fmt='o', marker=markers[idx], label=conversion_names_label[quantity_plot],
                        capsize=10, **kwargs)
            error_total.append(errors)

    if annotate:
        for _, values_plot in dict_totals_plot.items():  # this iterates over char, gas, fid and total.
            # this iterates over a temperatures, and one of the above getting a pair (T, yield)
            for x_axis_value, value_plot, annotation in zip(x_axis, values_plot, annotations):
                ax.annotate(annotation, (x_axis_value, value_plot), fontsize=16, alpha=0.5)
    if legend:
        ax.legend(loc='best')

    ax.set_ylabel('Yield, wt.\\%')
    ax.set_xlabel('Temperature, \N{DEGREE SIGN}C')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax

def plot_total_globals_difference(list_totals_dict, x_axis=None, save_plot=None, annotate=False,
                       errorbars=None, ax=None, fig=None, legend=True, **kwargs):
    """
    Function to wrap compare_group_totals to only plot the global totals (char, gas and FID)

    Parameters
    ----------
    list_totals_dict: list of dfs
        List of dicts with the totals.
    annotate: bool
        annotates the filenames
    save_plot: bool or str
        Save to a file with this name
    x_axis: None or 1D array
        to be used as x axis, if not given will use temperature of 1st reactor
    errorbars: None, False or dict
        If none or false, nothing shows. If a dict, will use it as % of the plotted quantities to create errorbars

    Return
    ----------
    fig: plt.figure
        matplolib figure for further modifications/saving
    ax: plt.axis
        matplotlib axis for further modifications/saving
    """
    plt.gca().set_prop_cycle(None)

    markers = get_markers()

    if ax is None:
        fig, ax = plt.subplots()

    yield_names = ('char_yield',  'total_gases', 'total_FID')
    dict_totals_plot = {'char_yield': [], 'total_gases': [], 'total_FID': [],  'total_non_quantified': []}
    annotations = []

    for dict_totals in list_totals_dict:
        yields = []  # container to add the yields of a single measurement (gas, char, fid)
        for yield_to_add in yield_names:
            extracted_yield_from_json = dict_totals.get(yield_to_add, np.nan)  # get it from the json file
            yields.append(extracted_yield_from_json)  # add it to the container
            dict_totals_plot[yield_to_add].append(extracted_yield_from_json)  # add it to the dictionary

        total = 100-np.nansum(yields)  # adds all of them considering nans = 0
        dict_totals_plot['total_non_quantified'].append(total)
        if annotate:
            mass = f'{dict_totals["mass ug"]:.0f} ug' if not np.isnan(dict_totals["mass ug"]) else ''
            first_react = f'{dict_totals["1st_react_temp"]:.0f} C' if not np.isnan(
                dict_totals["1st_react_temp"]) else ''
            second_react = f'{dict_totals["2nd_react_temp"]:.0f} C' if not np.isnan(
                dict_totals["2nd_react_temp"]) else ''
            annotations.append(f'{mass} {first_react} {second_react}')

    conversion_names_label = {'char_yield': 'Char',
                              'total_gases': 'Light Gases', 'total_FID': 'Vapors within GC range', 'total_non_quantified': 'Vapors outside GC range'}

    if x_axis is None:
        # x axis will be set to the temperature of the first reactor
        x_axis = []
        for dict_totals in list_totals_dict:
            x_axis.append(dict_totals['1st_react_temp'])

    if not errorbars:
        for idx, (quantity_plot, values_plot) in enumerate(dict_totals_plot.items()):
            ax.scatter(x_axis, values_plot, label=conversion_names_label[quantity_plot], marker=markers[idx], **kwargs)

    if errorbars:
        error_total = []
        for idx, (quantity_plot, values_plot) in enumerate(dict_totals_plot.items()):
            errors = np.array(values_plot) * errorbars[quantity_plot] / 100
            if quantity_plot == 'total_non_quantified':
                errors = np.sqrt(np.sum(np.square(error_total), axis=0))
            ax.errorbar(x_axis, values_plot, yerr=errors, fmt='o', marker=markers[idx], label=conversion_names_label[quantity_plot],
                        capsize=10, **kwargs)
            error_total.append(errors)

    if annotate:
        for _, values_plot in dict_totals_plot.items():  # this iterates over char, gas, fid and total.
            # this iterates over a temperatures, and one of the above getting a pair (T, yield)
            for x_axis_value, value_plot, annotation in zip(x_axis, values_plot, annotations):
                ax.annotate(annotation, (x_axis_value, value_plot), fontsize=16, alpha=0.5)
    if legend:
        ax.legend(loc='best')

    ax.set_ylabel('Yield, wt.\\%')
    ax.set_xlabel('Temperature, \N{DEGREE SIGN}C')
    if save_plot:
        fig.savefig(save_plot)

    return fig, ax
