import micropyro as mp

# read the database
database = mp.ReadDatabase.from_csv('database_example.csv')

# read the experimental matrix
exp_matrix = mp.ReadExperimentTable.from_csv("experimental_matrix.csv", header=0, use_is=True)
exp_matrix.compute_is_amount(concentration=0.03)

# get the blob dfs
dfs = []
temperatures = []
for row_name, row in exp_matrix.df.iterrows():
    # print(row_name)
    blob_file = mp.read_blob_file(f'{row_name}.cdf_img01_Blob_Table.csv')
    mp.perform_matching_database(blob_df=blob_file, database_df=database.df, extra_columns=['group'])
    blob_file = mp.compute_yields_is(experiment_df_row=row, blob_df=blob_file,
                                      internal_standard_name='fluoranthene')

    temperatures.append(row['temperature'])
    # print(blob_file['yield mrf'].nlargest(5))
    dfs.append(blob_file)


fig, ax = mp.compare_yields(dfs, compounds=['phenol', 'p-cresol', "benzene"], x_axis = temperatures)
ax.set_xlabel('Reactor Temperature, C')
ax.set_ylabel('Yield, %')
fig.savefig('comparison.pdf')