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

# def read_gas_yields(filename, sheet_name=0, **kwargs):
#     """
#     Retrieve the gas yields from an excel file and perform some cleanup.
#     Uses the :func:read_yields_excel to read.
#
#     Parameters
#     ----------
#     filename: str
#             File to read
#     sheet_name: str
#             Name of the sheet to read
#     kwargs
#             Extra arguments compliant with the read_xls of pandas.
#
#     Returns
#     -------
#     gas_data: df
#             DataFrame with the char yields, the temperature and some other properties
#
#     Examples
#     ---------
#     mp.read_yields_excel(filename='Micropyrolysis.xlsx',
#                     sheet_name='char yield measurement', skiprows=1, header=0)
#     """
#     experiment = mp.ReadExperimentTable.from_xls(filename, sheet_name=sheet_name,
#                                                  use_is=False, **kwargs)
#
#     char_data = experiment.df
#     return char_data
