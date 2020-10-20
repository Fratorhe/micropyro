import pandas as pd


def read_blob_file(filename):
    blob_file = pd.read_csv(filename, index_col=1)
    blob_file = blob_file[blob_file.Inclusion]
    blob_file.drop(['BlobID', 'Group Name', 'Inclusion', 'Internal Standard', "Retention I (min)", "Retention II (sec)",
                    "Peak Value", "Area (pixel count)"], axis=1, inplace=True)
    blob_file.index = blob_file.index.str.lower()  # puts everything in lower case to avoid repetitions and missmatching
    blob_file.index = [compound.strip() for compound in blob_file.index.values]
    blob_file.columns = blob_file.columns.str.lower()
    return blob_file


def define_internal_standard(blob_dataframe):
    pass


def check_matches_database(blob_df, database_df):
    for compound, _ in blob_df.iterrows():
        check_match_database(compound, database_df)


def check_match_database(compound, database_df):
    if compound not in database_df.index:
        print(f'{compound} not found in database')
        return False
    else:
        return True


def perform_matching_database(blob_df, database_df):
    # get all the columns from the database that start with the word group
    columns_grouping = [group for group in list(database_df.columns.values) if group.startswith("group")]

    # the columns to add to the blob_df will be the groups and teh other required data (MW, ECN, MRF).
    columns_copy = ["mw", "ecn", "mrf"] + columns_grouping

    # initialize the new columns to nans
    for column in columns_copy:
        blob_df[column] = "nan"

    for compound, _ in blob_df.iterrows():
        if check_match_database(compound, database_df):
            for column in columns_copy:
                blob_df.loc[compound, column] = database_df.loc[compound, column]
