import micropyro as mp

# Define the filename to work with
filename = '100 ug Py_600C-R_350C'

# read the database
database = mp.ReadDatabase.from_csv('database_example.csv')
print(database.df)

# read the blob file
blob_file = mp.read_blob_file(f'{filename}.cdf_img01_Blob_Table.csv')
mp.perform_matching_database(blob_df=blob_file, database_df=database.df, extra_columns=['group'])

# read the experimental matrix
exp_matrix = mp.ReadExperimentTable.from_csv("experimental_matrix.csv", header=0, use_is=True)
exp_matrix.compute_is_amount(concentration=0.03)
# grab the row of interest
exp_matrix_row = exp_matrix.df.loc[filename.lower()] # we need it in lowercase to avoid confusion
print(f'data from the experiment: {exp_matrix_row}')

# finally we compute the yields using the internal standard
results_df = mp.compute_yields_is(experiment_df_row=exp_matrix_row, blob_df=blob_file, internal_standard_name='fluoranthene')
mp.save_results_yields(blob_df=results_df, filename=f'{filename}.results.csv')

# we can easily access to the first 5 compounds with higher % yield
print(results_df['yield mrf'].nlargest(5))

# we can plot them as well
mp.plot_n_highest_yields(results_df, 5)

# or get a summary in terms of yields
sum_groups, total = mp.get_yields_summary(results_df, "group", to_file=f'{filename}.totals.csv')
print(f'The different groups are: {sum_groups}')
print(f'The total FID yield is: {total}')