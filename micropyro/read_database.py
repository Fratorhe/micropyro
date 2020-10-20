import re

import pandas as pd


class ReadDatabaseMicropyro():
    def __init__(self, database=None):
        if database is None:
            self.database = pd.DataFrame()
        else:
            self.database = database

        # put everything in lower case to avoid problems
        self.database.index = self.database.index.str.lower()
        self.database.columns = self.database.columns.str.lower()
        self.database.formula = self.database.formula.str.lower()
        self.database.index = [compound.strip() for compound in self.database.index.values]

        self.atoms = ['c', 'h', 'o', 'n']  # This could be extended if needed

        self.process_chon()
        self.process_ecn_mrf()

    @classmethod
    def from_excel(cls, filename):
        """
        This class method builds the database from an excel file.
        Should contain Compound as first column. Remaining columns should be MW, Formula, N_Benz, and any grouping.
        These columns do not have to be in any specific order, but to respect the name.
        :param filename:
        :return:
        """
        database = pd.read_excel(filename, index_col=0,
                                 converters={'MW': float})  # reads the file and sets the first column as index
        database = database[database.index.notnull()]  # removes the extra rows with index NaN
        return cls(database)

    @classmethod
    def from_csv(cls, filename):
        """
        This class method builds the database from a csv file.
        Should contain Compound as first column. Remaining columns should be MW, Formula, N_Benz, and any grouping.
        These columns do not have to be in any specific order, but to respect the name.
        :param filename:
        :return:
        """
        raise NotImplementedError

    def process_chon(self):
        for atom in self.atoms:
            self.database[atom] = self.database.apply(lambda row: self.extract_atoms(row['formula'], atom), axis=1)

    def process_ecn_mrf(self):
        self.database['ecn'] = self.database.apply(lambda row: ReadDatabaseMicropyro._compute_ecn(row), axis=1)
        self.database['mrf'] = self.database.apply(lambda row: ReadDatabaseMicropyro._compute_mrf(row), axis=1)

    @staticmethod
    def _compute_ecn(row):
        return int(row['c'])

    @staticmethod
    def _compute_mrf(row):
        combust = ReadDatabaseMicropyro._compute_combust(row['c'], row['h'], row['o'], row['n'])
        n_benz = row['n_benz']
        mrf = -0.071 + 0.000857 * combust + n_benz * 0.127
        return float(mrf)

    @staticmethod
    def _compute_combust(c, h, o, n):
        combust = 11.6 + 103.57 * c + 21.85 * h - 48.18 * o + 7.46 * n
        return combust

    @staticmethod
    def extract_atoms(formula, atom):
        # ensure small caps for everything
        formula = formula.lower()
        atom = atom.lower()
        # actual processing
        num_atoms = re.findall(f'{atom}[0-9]+|{atom}', formula)
        try:
            num_atoms = int(num_atoms[0][1:])
        except ValueError:
            num_atoms = 1
        except IndexError:
            num_atoms = 0
        return num_atoms
