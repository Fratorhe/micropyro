import warnings

import micropyro as mp


def read_yields_excel(filename, sheet_name=0, **kwargs):
    """
    Retrieve the char or light gases yields from an excel file.
    Turns negative numbers to 0.

    Parameters
    ----------
    filename: str
            File to read
    sheet_name: str
            Name of the sheet to read
    kwargs
            Extra arguments compliant with the read_xls of pandas.

    Returns
    -------
    char_data: df
            DataFrame with the char yields, the temperature and some other properties

    Examples
    ---------
    >>> mp.read_yields_excel(filename='Micropyrolysis.xlsx', sheet_name='char yield measurement', skiprows=1, header=0)
    df
    """
    experiment = mp.ReadExperimentTable.from_xls(filename, sheet_name=sheet_name,
                                                 use_is=False, **kwargs)

    data = experiment.df

    data = data.select_dtypes(include='number').clip(lower=0)  # kills all negative numbers
    return data


def add_gas_yield_to_totals_json(gas_or_char_matrix):
    """
    Add the totals from the gas yields to the json file with the results.
    Adds the total, the different gases, and their elemental composition.

    Parameters
    ----------
    gas_or_char_matrix
    """
    # we do it for each experiment
    cols_to_remove = ('t py', 'temperature')
    gas_or_char_matrix = gas_or_char_matrix.drop(cols_to_remove, errors='ignore', axis=1)

    # get all the json files

    for experiment, row in gas_or_char_matrix.iterrows():
        total_gases = row.sum()

        atoms_gases = compute_elemental_composition_gases(row)

        dict_data_yields = {'total_gases': total_gases, 'light_gases': dict(row),
                            'atoms_gases': atoms_gases}
        filename = mp.get_actual_filename(f'{experiment}.totals.json')

        if filename is not None:
            mp.append_json(filename, dict_data_yields)


# def add_char_yield_to_totals_json(gas_or_char_matrix):
#     cols_to_add = '% char'
#     add_yields_to_totals_json(gas_or_char_matrix, cols_to_add)
#
#
# def add_gas_yield_to_totals_json(gas_or_char_matrix, extra_cols_to_remove=()):
#     col_names = gas_or_char_matrix.columns
#
#     cols_to_remove = ('t py', 'temperature') + extra_cols_to_remove
#
#     cols_to_add = set(col_names) - set(cols_to_remove)
#     print(cols_to_add)
#
#     add_yields_to_totals_json(gas_or_char_matrix, cols_to_add)


def compute_elemental_composition_gases(row_experiment):
    """
    Compute the elemental composition of the yields from the light gases

    Parameters
    ----------
    row_experiment: pandas.Series
        with the different gases and their gas yield

    Returns
    -------
    yield_atoms: dict
        with the yields per atom

    """
    data_atoms = mp.get_atom_mw_dict()
    database = mp.ReadDatabase.from_internal().df
    database_cols = database.columns
    gases = row_experiment.keys()

    yield_atoms = {}
    for atom in data_atoms.keys():
        if atom in database_cols:
            yield_atom = 0 # we set it to 0 when we start
            for gas in gases:
                # find the gas the database
                n_atoms = database.loc[gas, atom]
                mw_gas = float(database.loc[gas, 'mw'])
                mw_atom = data_atoms[atom]['mw']

                yield_atom += row_experiment[gas] / mw_gas * n_atoms * mw_atom

            yield_atoms[atom] = yield_atom

    return yield_atoms
