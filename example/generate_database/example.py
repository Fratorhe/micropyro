import micropyro as mp

database = mp.GenerateDatabase.from_csv('database_example.csv')
database.get_formula_mw()

print(database._obtain_n_benz("C1=CC=C(C(=C1)C2=CC(=CC=C2)O)O"))

database.get_benzene_rings()

print(database.df)

database.to_csv()