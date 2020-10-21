import warnings

import pandas as pd


class ReadExperimentTable:
    """
    A class used to read experimental matrix typically done in micropyrolysis
    The idea is to have different constructors to create the df (csv, json, xls, etc).
    Each constructor should return the appropriate pandas dataframe as described in the test cases.
    All mass should be given in **mg**.
    ...

    Attributes
    ----------
    experiment_df : df
        a pandas dataframe with the information on the various experiments performed.
    used_is : bool
        define if internal standard was used (True) or not (False)

    Methods
    -------
    from_xls(cls, filename, sheet_name=0, use_is=True, **kwargs)
        Class method to load a xls file
    from_json(cls)
        Class method to load a json file (not available yet)
    from_dict(cls, filename, sheet_name=0, use_is=True, **kwargs)
        Class method to load a dict
    """

    def __init__(self, experiment_df, used_is):
        """
        Defines the dataframe of the experiments.
        Sets all the characters to lower case to avoid duplicity or mismatches with database.
        :param experiment_df: dataframe with the appropriate columns (see examples)
        :param used_is: bool internal standard used or not.
        """
        self.experiment_df = experiment_df

        # set all column headers in lower case to ensure there is no mistake
        self.experiment_df.index = self.experiment_df.index.str.lower()
        self.experiment_df.columns = self.experiment_df.columns.str.lower()
        self.experiment_df.index.name = self.experiment_df.index.name.lower()

        self.used_is = used_is

    @classmethod
    def from_xls(cls, filename, sheet_name=0, use_is=True, **kwargs):
        """
        Class method to read an file from excel with the data.
        User can specify the sheet, the use of internal standard, or any other kwargs supported by pandas.read_excel()
        :param filename: str.
                    name of the file to be read.
        :param sheet_name: str.
                    name of the sheet.
        :param use_is: bool.
        :param kwargs:
                    any kwargs valid for pandas.read_excel can be passed here. For example the range to be read.
        :return:
        """

        # reads the file
        experiment_df = pd.read_excel(filename, sheet_name, **kwargs)
        # removes the rows with nans in the filename.
        experiment_df = experiment_df[experiment_df['Filename'].notna()]
        # sets the index filename, so it is easier to refer to a specific experiment.
        experiment_df = experiment_df.set_index('Filename')
        # remove the mg from the name of the column, and removed any extra spaces
        experiment_df.columns = [col.replace("(mg)", "").strip() for col in experiment_df.columns]

        # create a copy of the temperature T (C) column for easier access through the code.
        experiment_df["temperature"] = experiment_df["T (C)"]

        return cls(experiment_df, use_is)

    @classmethod
    def from_json(cls):
        """
        read from json
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls):
        """
        read from a dict
        """
        raise NotImplementedError

    def compute_is_amount(self, concentration):
        """
        Compute the amount of internal standard given the concentration.
        Typically, we use a mixture of a known standard and a non reacting material (Al2O3).
        This is done to have better precision when measuring mass of IS.
        If only the standard is used, set concentration to 1, and no problem.
        :param concentration: float
                Concentration of the standard in the mixture.
        """
        if not self.used_is:
            warnings.warn("Internal Standard is set to False, not sure if what you are doing is correct...")
        self.experiment_df["is_amount"] = self.experiment_df.apply(lambda row: row['is'] * concentration, axis=1)

    def compute_char(self):
        """
        Computes the char content in mass (mg) and percent (%).
        """

        # delete the columns they already exist
        try:
            self.experiment_df.drop(["total before w/o holder", 'char mass', '% char'], inplace=True)
        except KeyError:
            pass
        # maybe the wool was not added, if so, we set it to 0
        if 'wool' not in self.experiment_df:
            self.experiment_df["wool"] = 0
        # maybe the is was not used
        if not self.used_is:
            self.experiment_df["is"] = 0
            self.experiment_df["is_amount"] = 0

        # compute the mass before without using the holder
        self.experiment_df["total before w/o holder"] = self.experiment_df["cup"] + self.experiment_df["sample"] + \
                                                        self.experiment_df["wool"] + self.experiment_df["hook"] + \
                                                        self.experiment_df["is"]

        # compute the mass of the char
        self.experiment_df["char mass"] = self.experiment_df["sample"] + self.experiment_df["is_amount"] + \
                                          self.experiment_df["total after w/o holder"] - \
                                          self.experiment_df["total before w/o holder"]

        # express it as % of the initial sample mass.
        self.experiment_df["% char"] = self.experiment_df["char mass"].values / self.experiment_df[
            "sample"].values * 100
