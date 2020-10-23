import pandas as pd


def read_blob_file(filename, drop_useless_columns=True, index_col=1):
    """
    Reads a blob file (CSV) from GC Image software.

    Parameters
    ----------
    filename: str
            blob file to be read.
    drop_useless_columns: bool.
            drop some columns from the dataframe which are not used. TODO: revisit if some may be useful (retention time?)
    index_col: int
            Column number to be used as index. Defaults to 1 because GC Image gives the ID as first column,
            but for postprocessing we need the 0.

    Returns
    ---------
    blob_file: df
            with the blob file.
    """
    blob_file = pd.read_csv(filename, index_col=index_col)
    try:
        blob_file = blob_file[blob_file.Inclusion]
    except AttributeError:
        pass

    if drop_useless_columns:
        # try to remove the columns, otherwise just leave them..either they don't exist, or we don't care anyway.
        try:
            blob_file.drop(
                ['BlobID', 'Group Name', 'Inclusion', 'Internal Standard', "Retention I (min)", "Retention II (sec)",
                 "Peak Value", "Area (pixel count)"], axis=1, inplace=True)
        except KeyError:
            pass

    blob_file.index = blob_file.index.str.lower()  # puts everything in lower case to avoid repetitions and missmatching

    blob_file = blob_file[blob_file.index.notnull()]  # removes the extra rows with index NaN

    blob_file.index = [compound.strip() for compound in blob_file.index.values]
    blob_file.columns = blob_file.columns.str.lower()
    return blob_file


def check_matches_database(blob_df, database_df):
    """
    Function to check matches with the df. Only provides the name of **not found compounds**.
    Can be used when new files are introduced.

    Parameters
    ----------
    blob_df: dataframe
            Read using read_blob_file
    database_df: dataframe
            Created with the class ReadDatabase
    """
    for compound, _ in blob_df.iterrows():
        check_match_database(compound, database_df)


def check_match_database(compound, database_df):
    """
    Function to check if a compound is in the df.

    Parameters
    ----------
    compound: str
            Name of the compound to search for
    database_df: pandas dataframe
            Dataframe with the different compounds.

    Returns
    ---------
    Bool
        Exists or not
    """
    if compound not in database_df.index:
        print(f'{compound} not found in df')
        return False
    else:
        return True


def perform_matching_database(blob_df, database_df, extra_columns=None):
    """
    Function to perform the matching with the df. If the match is correct,
    it will copy the required properties to the blob_df.

    Parameters
    ----------
    blob_df: pandas dataframe
                Read using read_blob_file
    database_df: pandas dataframe
                Dataframe with the different compounds.
    extra_columns: list of str
                Extra columns to be copied from the df to the blob_df
                (maybe some gouping or "c", "h", "o", etc. if intending to do elemental balance)

    """
    # get all the columns from the df that start with the word group
    if extra_columns is None:
        extra_columns = []
    # columns_grouping = [group for group in list(database_df.columns.values) if group.startswith("group")]

    # the columns to add to the blob_df will be the groups and teh other required data (MW, ECN, MRF).
    columns_copy = ["mw", "ecn", "mrf"] + extra_columns

    # initialize the new columns to nans
    for column in columns_copy:
        blob_df[column] = "nan"

    # for each compound, match with the df adding the corresponding values to the columns.
    for compound, _ in blob_df.iterrows():
        if check_match_database(compound, database_df):
            for column in columns_copy:
                blob_df.loc[compound, column] = database_df.loc[compound, column]
