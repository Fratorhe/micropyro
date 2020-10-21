def compute_yields_is(experiment_df_row, blob_df, internal_standard_name):
    """

    :param experiment_df_row:
    :param blob_df:
    :param internal_standard_name:
    :return:
    """
    sample_mass = experiment_df_row['sample']

    # get the internal standard compound and drop it from the original dataframe.
    # it requires a different treatment
    internal_standard = define_internal_standard(experiment_df_row, blob_df, internal_standard_name)
    blob_df.drop(internal_standard_name, inplace=True)

    blob_df["moles ecn"] = blob_df.apply(
        lambda row: row.volume * internal_standard.moles / internal_standard.volume * internal_standard.ecn / float(
            row.ecn),
        axis=1)

    blob_df["moles mrf"] = blob_df.apply(
        lambda row: row.volume * internal_standard.moles / internal_standard.volume * internal_standard.mrf / float(
            row.mrf),
        axis=1)

    blob_df["mass mrf"] = blob_df.apply(lambda row: row["moles mrf"] * float(row["mw"]) * 1000, axis=1)
    blob_df["yield mrf"] = blob_df.apply(lambda row: row["mass mrf"] / sample_mass * 100, axis=1)

    return blob_df


def define_internal_standard(experiment_df_row, blob_df, internal_standard_name):
    """

    :param experiment_df_row:
    :param blob_df:
    :param internal_standard_name:
    :return:
    """
    internal_standard = blob_df.loc[internal_standard_name].copy()
    mass_IS = experiment_df_row.is_amount
    internal_standard['moles'] = (mass_IS / 1000) / internal_standard.mw
    return internal_standard


def save_results_yields(blob_df, filename):
    """

    :param blob_df:
    :param filename:
    """
    blob_df.to_csv(filename)
