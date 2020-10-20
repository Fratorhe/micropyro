import pandas as pd


def read_blob_file(filename):
    blob_file = pd.read_csv(filename, index_col=1)
    blob_file = blob_file[blob_file.Inclusion]
    blob_file.drop(['BlobID', 'Group Name', 'Inclusion'], axis=1, inplace=True)
    blob_file.index = blob_file.index.str.lower()  # puts everything in lower case to avoid repetitions and missmatching
    return blob_file


def define_internal_standard(blob_dataframe):
    pass


def check_matches_database(blob_file_df, database_df):
    for compound, _ in blob_file_df.iterrows():
        if compound not in database_df.index:
            print(f'{compound} not found in database')


# def match_with_database(blob_file_df, database_df):
#     for compound, _ in blob_file_df.iterrows():

def compute_yields(experiment_data, blob_table):
    pass