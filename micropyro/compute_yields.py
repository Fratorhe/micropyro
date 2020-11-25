import json


def define_internal_standard(experiment_df_row, blob_df, internal_standard_name, calibration_file=None):
    """
    Grabs the internal standard from the blob_df and from the experiment df to
    combine them and have all the required data together.
    This function is not usually used directly, but by compute_yields_is.

    Parameters
    ----------
    experiment_df_row: df row.
                of the experiment being analyzed.
    blob_df: df
                dataframe after being processed with.
    internal_standard_name: str
                Name of the internal standard compound.

    Returns
    ----------
    internal_standard: df row
            Data of the internal standard in a pandas dataframe row.
    """
    try:
        internal_standard = blob_df.loc[internal_standard_name].copy()
    except KeyError:
        raise FileNotFoundError(f'Internal Standard "{internal_standard_name}" not found in this blob table')



    volume_blob_is = internal_standard.volume
    if calibration_file:
        mass_IS = get_mass_calibration(calibration_file, volume_blob_is)
    else:
        mass_IS = experiment_df_row.is_amount
    internal_standard['moles'] = (mass_IS / 1000) / internal_standard.mw
    return internal_standard


def get_mass_calibration(calibration_file, volume):
    """
    This function computes the mass given a calibration curve: mass = a / vol.

    Parameters
    ----------
    calibration_file: str
        filename of the json file with the slope of the calibration curve
    volume: float
        volume of the blob from GC Image

    Returns
    --------
    mass_IS: float
        mass of the compound used as refernece.
    """
    with open(calibration_file) as fp:
        data = json.load(fp)
    slope = float(data["slope"])
    mass_IS = volume / slope
    return mass_IS


def compute_yields(experiment_df_row, blob_df, internal_standard_name, calibration_file, compounds_drop):
    """
    Generic function to compute the yields of an experiment from an internal standard.
    Requires the experiment, the blob file and the name of the internal standard used.
    User does not have to use this function, but the particular ones below.
    Updates teh blob_df adding the following columns:

    - **moles ecn**: moles of compound using the ecn method.

    - **moles mrf**: moles of compound using the mrf method.

    - **mass mrf**: mass (mg) of compound using mrf method.

    - **yield mrf**: % wrt sample mass.

    Parameters
    ----------
    calibration_file: str
        Path to the calibration file
    compounds_drop: list
        List of compounds to drop
    experiment_df_row: row of a dataframe
                with experiments from micropyrolysis. Created using ReadExperimentTable.
    blob_df: df
                with the blobs after performing the df matching.
    internal_standard_name: str
                name of the internal standard used.

    Returns
    ----------
    blob_df
        with updated columns
    """

    # extract the sample mass
    sample_mass = experiment_df_row['sample']

    # process duplicates
    all_columns = set(blob_df.columns)
    colums_to_sum = {'volume'} # set of columns to sum if duplicates
    columns_stay_same = all_columns-colums_to_sum

    dict_to_sum = {key: sum for key in colums_to_sum}
    dict_stay_same = {key: 'first' for key in columns_stay_same}
    dict_aggregate = {**dict_to_sum, **dict_stay_same}

    blob_df = blob_df.groupby(blob_df.index).agg(dict_aggregate)

    # get the internal standard compound and drop it from the original dataframe.
    # it requires a different treatment
    internal_standard = define_internal_standard(experiment_df_row, blob_df, internal_standard_name, calibration_file)

    if compounds_drop is not None:
        for compound in compounds_drop:
            try:
                blob_df.drop(compound, inplace=True)
            except KeyError:
                print(f'{compound} not found to drop')

    # compute the moles using the ecn for each compound and add it in a new column
    blob_df["moles ecn"] = blob_df.apply(
        lambda row: row.volume * internal_standard.moles / internal_standard.volume * internal_standard.ecn / float(
            row.ecn),
        axis=1)

    # compute the moles using the mrf for each compound and add it in a new column
    blob_df["moles mrf"] = blob_df.apply(
        lambda row: row.volume * internal_standard.moles / internal_standard.volume * internal_standard.mrf / float(
            row.mrf),
        axis=1)

    # compute the mass using the mrf for each compound and add it in a new column
    blob_df["mass mrf"] = blob_df.apply(lambda row: row["moles mrf"] * float(row["mw"]) * 1000, axis=1)
    # compute the yield using the mrf for each compound and add it in a new column in percent
    blob_df["yield mrf"] = blob_df.apply(lambda row: row["mass mrf"] / sample_mass * 100, axis=1)

    return blob_df


def compute_yields_is(experiment_df_row, blob_df, internal_standard_name):
    """
    Particular function to compute the yields using an IS.
    The IS will be removed from the blob_df, but the yields will be based on its mass.
    For the implementation, see compute_yields.

    #TODO: this function may give problems with compounds that we need to drop (repeated in FID and special gc)

    Returns
    -------
    blob_df: df
        Dataframe with the blobs, with the extra column of yields
    """
    blob_df = compute_yields(experiment_df_row, blob_df, internal_standard_name, calibration_file=None,
                             compounds_drop=internal_standard_name)
    return blob_df


def compute_yields_calibration(experiment_df_row, blob_df, reference_compound, calibration_file, compounds_drop=None):
    """
    Particular function to compute the yields using a calibration curve of a reference compound.
    In this case, the mass of reference compound is computed using an the auxiliary function get_mass_calibration.
    User can still define compounds_drop since in many cases, one uses both an external calibration and an Internal Standard.
    For the implementation, see compute_yields.

    Returns
    -------
    blob_df: df
        Dataframe with the blobs, with the extra column of yields
    """
    blob_df = compute_yields(experiment_df_row, blob_df, internal_standard_name=reference_compound,
                             calibration_file=calibration_file,
                             compounds_drop=compounds_drop)
    return blob_df


def save_results_yields(blob_df, filename):
    """
    Save the resulting blob_df to a new file.

    Parameters
    ----------
    blob_df: df
    filename: str
            name of the output file.
    """
    blob_df.to_csv(filename)
