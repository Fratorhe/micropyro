import math
import re
from shutil import copyfile

import pandas as pd
import numpy as np
import pubchempy
from tqdm import tqdm
from openbabel import openbabel

class GenerateDatabase:
    """
    A class used to generate a database for micropyrolysis computations from a file with compound names.
    ...


    Attributes
    ----------
    database : df
        a pandas dataframe with the actual df

    Methods
    -------------
    from_xls(cls, filename, **kwargs)
        Class method to load a xls file. Accepts kwargs for pandas.read_excel.
    from_csv(cls)
        Class method to load a csv file (not available yet).
    process_chon(self)
        Retrieves the number of carbons, hydrogen, oxygen and nitrogen for the different compounds in the df.
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
        database = pd.read_excel(filename, index_col=0,**kwargs)  # reads the file and sets the first column as index
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
        database = pd.read_csv(filename, index_col=0,**kwargs)  # reads the file and sets the first column as index
        database = database[database.index.notnull()]  # removes the extra rows with index NaN
        return cls(database, filename)

    def get_formula_mw(self):
        for compound, _ in tqdm(self.df.iterrows(), total=self.df.shape[0]):
            ## get the compound from pubchempy
            compound_pubchem = self.get_compound_pubchem(compound)

            if compound_pubchem is not None:
                self.df.loc[compound,'mw'] = compound_pubchem.molecular_weight
                self.df.loc[compound,'formula'] = compound_pubchem.molecular_formula
                self.df.loc[compound,'smiles'] = compound_pubchem.isomeric_smiles


    @staticmethod
    def get_compound_pubchem(compound_name):
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
        for compound, row in tqdm(self.df.iterrows(), total=self.df.shape[0]):
            ## get the compound from pubchempy
            smiles = row['smiles']
            try:
                n_Benz = self.obtain_n_benz(smiles)
            except TypeError:
                n_Benz = -1

            self.df.loc[compound,'n_benz'] = n_Benz

    @staticmethod
    def obtain_n_benz(compound_smiles):
        mol = openbabel.OBMol()
        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("smi", "mdl")
        obConversion.ReadString(mol, compound_smiles)
        n_aromatic_rings = 0
        for ring in mol.GetSSSR():
            if ring.IsAromatic() and ring.Size()>5:
                n_aromatic_rings +=1
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
