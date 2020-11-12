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
    data.update(data.select_dtypes(include='number').clip(lower=0))  # kills all negative numbers
    return data


def add_gas_yield_to_totals_json(gas_yield_matrix):
    """
    Add the totals from the gas yields to the json file with the results.
    Adds the total, the different gases, and their elemental composition.

    Parameters
    ----------
    gas_yield_matrix
    """
    # we do it for each experiment
    cols_to_remove = ['t py', 'temperature', 't (c)']
    gas_yield_matrix = gas_yield_matrix.drop(cols_to_remove, errors='ignore', axis=1)

    # get all the json files

    for experiment, row in gas_yield_matrix.iterrows():
        total_gases = row.sum()

        atoms_gases = compute_elemental_composition_gases(row)

        dict_data_yields = {'total_gases': total_gases, 'light_gases': dict(row),
                            'atoms_gases': atoms_gases}
        filename = mp.get_actual_filename(f'{experiment}.totals.json')

        if filename is not None:
            mp.append_json(filename, dict_data_yields)
            print(f'Added data to {experiment}')

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
            yield_atom = 0  # we set it to 0 when we start
            for gas in gases:
                # find the gas the database
                n_atoms = database.loc[gas, atom]
                mw_gas = float(database.loc[gas, 'mw'])
                mw_atom = data_atoms[atom]['mw']

                yield_atom += row_experiment[gas] / mw_gas * n_atoms * mw_atom

            yield_atoms[atom] = yield_atom

    return yield_atoms

def add_char_yield_to_totals_json(char_yield_matrix, in_percent=True):
    """
    Add the char yield to the json file with the results.

    Parameters
    ----------
    char_yield_matrix: pandas.df
            Char matrix read using the class :meth:`micropyro.ReadExperimentTable`
    in_percent
    """
    # we do it for each experiment
    cols_to_remove = ['t py', 'temperature', 't (c)']
    char_yield_matrix = char_yield_matrix.drop(cols_to_remove, errors='ignore', axis=1)

    # check if to mutiply it by 100 to have it in %
    if in_percent:
        to_percent = 100
    else:
        to_percent = 1

    # get all the json files
    for experiment, row in char_yield_matrix.iterrows():
        dict_data_yields = {'char_yield': row['% char']*to_percent}
        filename = mp.get_actual_filename(f'{experiment}.totals.json')

        if filename is not None:
            mp.append_json(filename, dict_data_yields)
            print(f'Added data to {experiment}')