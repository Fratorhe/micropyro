import warnings

import pandas as pd


class ReadExperimentTable:
    def __init__(self, experiment_df, used_is):
        """

        :param experiment_df:
        :param used_is:
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

        :param filename:
        :param sheet_name:
        :param use_is:
        :param kwargs:
        :return:
        """
        experiment_df = pd.read_excel(filename, sheet_name, **kwargs)
        experiment_df = experiment_df[experiment_df['Filename'].notna()]
        experiment_df = experiment_df.set_index('Filename')
        # remove the mg from the name of the column, and removed any extra spaces
        experiment_df.columns = [col.replace("(mg)", "").strip() for col in experiment_df.columns]

        experiment_df["temperature"] = experiment_df["T (C)"]

        return cls(experiment_df, use_is)

    @classmethod
    def from_json(cls):
        """

        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls):
        raise NotImplementedError

    def compute_is_amount(self, concentration):
        if not self.used_is:
            warnings.warn("Internal Standard is set to False, not sure if what you are doing is correct...")
        self.experiment_df["is_amount"] = self.experiment_df.apply(lambda row: row['is'] * concentration, axis=1)

    def compute_char(self):
        # delete the columns they already exist
        #
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

        self.experiment_df["total before w/o holder"] = self.experiment_df["cup"] + self.experiment_df["sample"] + \
                                                        self.experiment_df["wool"] + self.experiment_df["hook"] + \
                                                        self.experiment_df["is"]
        print(self.experiment_df["char mass"].values)

        self.experiment_df["char mass"] = self.experiment_df["sample"] + self.experiment_df["is_amount"] + \
                                          self.experiment_df["total after w/o holder"] - \
                                          self.experiment_df["total before w/o holder"]

        self.experiment_df["% char"] = self.experiment_df["char mass"].values / self.experiment_df[
            "sample"].values * 100
