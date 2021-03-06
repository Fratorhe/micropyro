import re

import pandas as pd
import numpy as np
import pkg_resources

class ReadDatabase:
    """
    A class used to read df for micropyrolysis computations.
    The idea is to have different constructors to create the df (csv, json, xls, google sheets, etc).
    Each constructor should return the appropriate pandas dataframe as described in the test cases.
    User should provide only the name of the compound, the empirical formula, the MW, and the number of benzene rings.
    TODO: this could be improved further by crating a scrapper that adds the compounds to the df directly.
    ...


    Attributes
    ----------
    database : df
        a pandas dataframe with the actual df
    atoms : tuple. Class attribute.
        atoms to be studied


    Methods
    -------------
    from_xls(cls, filename, **kwargs)
        Class method to load a xls file. Accepts kwargs for pandas.read_excel.
    from_csv(cls)
        Class method to load a csv file.
    from_internal(cls)
        Class method to load an internal database located in "package_folder"/data/Database_micropyro.csv.
    process_chon(self)
        Retrieves the number of carbons, hydrogen, oxygen and nitrogen for the different compounds in the df.
    process_ecn_mrf(self)
        Computes the ecn and the mrf. Uses _compute_ecn and _compute_mrf.
    _compute_ecn(row)
        Computes the effective carbon number for a given row (compound)
    _compute_mrf(row)
        Computes the mrf for a given row (compound), uses _compute_combust to perform the computations.
    _compute_combust(c, h, o, n)
        Computes the combustion for a given row (compound)
    _extract_atoms(formula, atom)
        Extracts atoms (c,h,o,n) from a given formula. Used by process_chon
    """

    atoms = ('c', 'h', 'o', 'n')  # This could be extended if needed

    def __init__(self, database=None):
        if database is None:
            self.df = pd.DataFrame()
        else:
            self.df = database

        # put everything in lower case to avoid problems
        self.df.index = self.df.index.str.lower()
        self.df.columns = self.df.columns.str.lower()
        self.df.formula = self.df.formula.str.lower()

        # drop extra rows with nans
        self.df = self.df[self.df.index.notnull()]  # removes the extra rows with index NaN
        self.df = self.df[self.df.formula.notnull()]  # removes the extra rows with index NaN

        # remove any extra trailing spaces
        self.df.index = [compound.strip() for compound in self.df.index.values]


        self.process_chon()
        self.process_ecn_mrf()

    @classmethod
    def from_xls(cls, filename, **kwargs):
        """
        This class method builds the df from an excel file.
        Should contain Compound as first column. Remaining columns should be MW, Formula, N_Benz, and any grouping.
        These columns do not have to be in any specific order, but to respect the name.
        :param filename: str
                filename (with path if needed) to the df file.
        :return: constructor for the class.
        """
        database = pd.read_excel(filename, index_col=0,
                                 converters={'MW': float},
                                 **kwargs)  # reads the file and sets the first column as index
        return cls(database)

    @classmethod
    def from_csv(cls, filename, **kwargs):
        """
        This class method builds the df from a csv file.
        Should contain Compound as first column. Remaining columns should be MW, Formula, N_Benz, and any grouping.
        These columns do not have to be in any specific order, but to respect the name.
        :param filename:
        :return: constructor for the class.
        """
        database = pd.read_csv(filename, index_col=0,
                                 converters={'MW': float},
                                 **kwargs)  # reads the file and sets the first column as index
        return cls(database)

    @classmethod
    def from_internal(cls):
        """
        This class method builds the df from the internal database.
        :return: constructor for the class.
        """
        DATA_PATH = pkg_resources.resource_filename('micropyro', 'databases/Database_micropyro.csv')

        database = pd.read_csv(DATA_PATH, index_col=0,
                                 converters={'MW': float})  # reads the file and sets the first column as index
        return cls(database)


    def process_chon(self):
        """
        For each atoms, extract the number from the empirical formula.
        This is directly applied to all the rows in the dataframe and saved in new df columns with the name of the atom.
        """
        for atom in self.atoms:
            self.df[atom] = self.df.apply(lambda row: self._extract_atoms(row['formula'], atom), axis=1)

    def process_ecn_mrf(self):
        """
        Computes the ecn and mrf for each row in the df. Uses the static methods _compute_ecn and _compute_mrf.
        """
        self.df['ecn'] = self.df.apply(lambda row: ReadDatabase._compute_ecn(row), axis=1)
        self.df['mrf'] = self.df.apply(lambda row: ReadDatabase._compute_mrf(row), axis=1)

    @staticmethod
    def _compute_ecn(row):
        """
        computes the ecn (which actually is the number of carbons normally).
        :param row: df row.
                of a compound in df.
        :return: int.
                number of carbons in the compound.
        """
        return int(row['c'])

    @staticmethod
    def _compute_mrf(row):
        """
        computes the mrf using an empirical formula.
        TODO: see if this formula is always the same, or depends on the internal standard used.
        :param row: df row.
                of a compound in df.
        :return: float.
                the value of the mrf.
        """
        combust = ReadDatabase._compute_combust(row['c'], row['h'], row['o'], row['n'])
        n_benz = row['n_benz']
        if np.isnan(n_benz):
            n_benz = 0
        mrf = -0.071 + 0.000857 * combust + n_benz * 0.127
        return float(mrf)

    @staticmethod
    def _compute_combust(c, h, o, n):
        """
        Computes the heat of combustion.
        :param c: number of carbons atoms
        :param h: number of hydrogen atoms
        :param o: number of oxygen atoms
        :param n: number of nitrogen atoms
        :return: heat of combustion for the given combination of atoms.
        """
        combust = 11.06 + 103.57 * c + 21.85 * h - 48.18 * o + 7.46 * n
        return combust

    @staticmethod
    def _extract_atoms(formula, atom):
        """
        Extract the number of the specified atom in a given empirical formula.
        :param formula: str
                Formula of a compound (eg. CH4)
        :param atom: str
                Atom to search C, H, N, O.
        :return: int
                number of atoms of the given atom in the formula.
        """
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
