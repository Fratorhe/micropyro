def compute_yields_is(experiment_df_row, blob_df, internal_standard_name):
    """
    Function to compute the yields of an experiment from an internal standard.
    Requires the experiment, the blob file and the name of the internal standard used.
    Updates teh blob_df adding the following columns:
    - moles ecn: moles of compound using the ecn method.
    - moles mrf: moles of compound using the mrf method.
    - mass mrf: mass (mg) of compound using mrf method.
    - yield mrf: % wrt sample mass.
    :param experiment_df_row: row of a dataframe
                with experiments from micropyrolysis. Created using ReadExperimentTable.
    :param blob_df: df
                with the blobs after performing the database matching.
    :param internal_standard_name: str
                name of the internal standard used.
    :return: blob_df with updated columns
    """

    # extract the sample mass
    sample_mass = experiment_df_row['sample']

    # get the internal standard compound and drop it from the original dataframe.
    # it requires a different treatment
    internal_standard = define_internal_standard(experiment_df_row, blob_df, internal_standard_name)
    blob_df.drop(internal_standard_name, inplace=True)

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


def define_internal_standard(experiment_df_row, blob_df, internal_standard_name):
    """
    Grabs the internal standard from the blob_df and from the experiment df to
    combine them and have all the required data together.
    This function is not usually used directly, but by compute_yields_is.
    :param experiment_df_row: df row.
                of the experiment being analyzed.
    :param blob_df: df
                dataframe after being processed with.
    :param internal_standard_name: str
                Name of the internal standard compound.
    :return:
    """
    internal_standard = blob_df.loc[internal_standard_name].copy()
    mass_IS = experiment_df_row.is_amount
    internal_standard['moles'] = (mass_IS / 1000) / internal_standard.mw
    return internal_standard


def save_results_yields(blob_df, filename):
    """
    Save the resulting blob_df to a new file.
    :param blob_df: df
    :param filename: str
            name of the output file.
    """
    blob_df.to_csv(filename)
