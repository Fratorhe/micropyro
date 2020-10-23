from shutil import copyfile

import pandas as pd
import pubchempy
from openbabel import openbabel
from tqdm import tqdm


class GenerateDatabase:
    """
    A class used to generate a database for micropyrolysis computations from a file with compound names.
    ...

    Attributes
    ----------
    df : df
        a pandas dataframe with the actual df
    filename : str
        filename of the database

    Methods
    -------------
    from_xls(cls, filename, **kwargs)
        Class method to load a xls file. Accepts kwargs for pandas.read_excel.
    from_csv(cls)
        Class method to load a csv file (not available yet).
    get_formula_mw(self)
        Retrieves the MW, formula and smiles for the different compounds in the df.
    get_benzene_rings(self)
        Retrieves the number of rings for the different compounds in the df.
    to_csv(self, backup=True)
        Exports the resulting df to a csv
    to_xls(self, backup=True)
        Exports the resulting df to a xls
    _get_compound_pubchem(compound_name)
        Actual compound finder from pubchempy
    _obtain_n_benz(compound_smiles)
        Actual ring counter
    _create_backup(self)
        Auxiliary function to create backup of files
    """

    def __init__(self, database, filename):
        if database is None:
            self.df = pd.DataFrame()
        else:
            self.df = database

        self.filename = filename

        # put everything in lower case to avoid problems
        self.df.index = self.df.index.str.lower()
        self.df.columns = self.df.columns.str.lower()
        self.df.index = [compound.strip() for compound in self.df.index.values]

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
        database = pd.read_excel(filename, index_col=0, **kwargs)  # reads the file and sets the first column as index
        database = database[database.index.notnull()]  # removes the extra rows with index NaN
        return cls(database, filename)

    @classmethod
    def from_csv(cls, filename, **kwargs):
        """
        This class method builds the df from a csv file.
        Should contain Compound as first column. Remaining columns should be MW, Formula, N_Benz, and any grouping.
        These columns do not have to be in any specific order, but to respect the name.
        :param filename:
        :return: constructor for the class.
        """
        database = pd.read_csv(filename, index_col=0, **kwargs)  # reads the file and sets the first column as index
        database = database[database.index.notnull()]  # removes the extra rows with index NaN
        return cls(database, filename)

    def get_formula_mw(self):
        """
        Get the formula, the molecular weight, and the smiles
        """
        not_founds = []
        for compound, _ in tqdm(self.df.iterrows(), total=self.df.shape[0]):
            ## get the compound from pubchempy
            compound_pubchem = self._get_compound_pubchem(compound)

            if compound_pubchem is not None:
                self.df.loc[compound, 'mw'] = compound_pubchem.molecular_weight
                self.df.loc[compound, 'formula'] = compound_pubchem.molecular_formula
                self.df.loc[compound, 'smiles'] = compound_pubchem.isomeric_smiles
            else:
                not_founds.append(compound)

        if not_founds:
            with open("not_founds.txt", 'w') as f:
                f.write("\n".join(map(str, not_founds)))

    @staticmethod
    def _get_compound_pubchem(compound_name):
        """
        Gets the compound from pubchempy

        Parameters
        -----------
        compound_name: str
            name of the compound

        Return
        ------
        """
        ## get the compound from pubchempy
        compound_pubchem = pubchempy.get_compounds(compound_name, 'name')
        # we take the first index, hopefully we are right in most cases because we are giving the specific name
        # if we don't get anything back, we return a -1 and the get_formula_mw will take care.
        try:
            cid = compound_pubchem[0].cid
        except IndexError:
            print(f'{compound_name} not found')
            return None

        object_compound = pubchempy.Compound.from_cid(cid)

        return object_compound

    def get_benzene_rings(self):
        """
        Gets the number of benzene rings for each compound.

        """
        for compound, row in tqdm(self.df.iterrows(), total=self.df.shape[0]):
            ## get the compound from pubchempy
            smiles = row['smiles']
            try:
                n_Benz = self._obtain_n_benz(smiles)
            except TypeError:
                n_Benz = -1

            self.df.loc[compound, 'n_benz'] = n_Benz

    @staticmethod
    def _obtain_n_benz(compound_smiles):
        """
        Gets the number of benzene rings from the smiles. Only added for benzene aromatic rings.

        Parameters
        -----------
        compound_smiles: str
            smiles of the compound

        Return
        ------
        n_aromatic_rings: int
            Number of aromatic rings
        """

        mol = openbabel.OBMol()
        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("smi", "mdl")
        obConversion.ReadString(mol, compound_smiles)
        n_aromatic_rings = 0
        for ring in mol.GetSSSR():
            if ring.IsAromatic() and ring.Size() > 5:
                n_aromatic_rings += 1
            # print(ring.Size(), ring.IsAromatic(), ring.GetType())
        return n_aromatic_rings

    def to_csv(self, backup=True):
        if backup:
            self._create_backup()
        self.df.to_csv(self.filename, index_label="compound")

    def to_xls(self, backup=True):
        if backup:
            self._create_backup()
        self.df.to_excel(self.filename, index_label="compound")

    def _create_backup(self):
        copyfile(self.filename, f'{self.filename}.bak')
