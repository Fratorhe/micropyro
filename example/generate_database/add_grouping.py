import micropyro as mp

database = mp.GenerateDatabase.from_csv('database_example.csv')

file_name = 'example_add_grouping.csv'

database.add_grouping(file_data=file_name, grouping_name='grouping_fran')

database.to_csv()