import json
import warnings

import pandas as pd
import numpy as np
from lmfit import Model
from sklearn.linear_model import LinearRegression, HuberRegressor
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.graphics as smgraphics
import statsmodels.api as smapi
import statsmodels.graphics as smgraphics
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.api import add_constant


class ExternalCalibration:
    """
    A class used to perform calibration typically done in micropyrolysis.
    So far, only the constructor through dataframe (__init__) or through excel (from_xls) are implemented.
    All mass should be given in **mg**.

    ...

    Attributes
    ----------
    calibration_df : df
        a pandas dataframe with the information on the various experiments performed.
    used_is : bool
        define if internal standard was used (True) or not (False)

    Methods
    -------
    from_xls(cls, filename, sheet_name=0, use_is=True, **kwargs)
        Class method to load a xls file

    """

    def __init__(self, calibration_df):
        """
        Defines the dataframe of the experiments.
        Sets all the characters to lower case to avoid duplicity or mismatches with database.

        :param calibration_df: dataframe with the appropriate columns (see examples)
        :param used_is: bool internal standard used or not.
        """
        self.calibration_df = calibration_df

        # set all column headers in lower case to ensure there is no mistake
        self.calibration_df.index = self.calibration_df.index.str.lower()
        self.calibration_df.columns = self.calibration_df.columns.str.lower()
        self.calibration_df.index.name = self.calibration_df.index.name.lower()

        self.remove_incomplete()

    @classmethod
    def from_xls(cls, filename, sheet_name=0, **kwargs):
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
        calibration_df = pd.read_excel(filename, sheet_name, **kwargs)
        # removes the rows with nans in the filename.
        calibration_df = calibration_df[calibration_df['Filename'].notna()]
        # sets the index filename, so it is easier to refer to a specific experiment.
        calibration_df = calibration_df.set_index('Filename')
        # remove the mg from the name of the column, and removed any extra spaces
        calibration_df.columns = [col.replace("(mg)", "").strip() for col in calibration_df.columns]

        return cls(calibration_df)

    def drop_point(self, index_name):
        """
        Method to remove specific points from the dataframe.
        User should provide the index (usually filename) of the point to drop.
        :param index_name: str.
                    name of the row to drop
        :return: None
        """

        self.calibration_df.drop(index_name, inplace=True)

    def remove_incomplete(self):
        """
        Sometimes the dataframe is incomplete (some measurements not done or something similar).
        Here, we specify that if some measurements are missing, we drop the row automatically.

        :return index_removed
                Indeces (experiment names) removed from the dataframe.
        """
        index_names_before = set(self.calibration_df.index.values.tolist())
        self.calibration_df = self.calibration_df[self.calibration_df['volume'].notna()]
        self.calibration_df = self.calibration_df[self.calibration_df['volume'].notna()]
        index_names_after = set(self.calibration_df.index.values.tolist())

        index_removed = index_names_before - index_names_after

        print(f"The following cases are removed because they are incomplete:")
        print(*index_removed, sep="\n")

        return index_removed

    def linear_calibration(self, outliers=[], to_file="calibration.json"):
        x = np.array(self.calibration_df["sample"].values)
        y = np.array(self.calibration_df["volume"].values)

        for outlier in outliers:
            index = np.argwhere(x == outlier)
            x = np.delete(x, index)
            y = np.delete(y, index)

        # # Fit data
        # if fit_intercept:
        #     x = add_constant(x)

        self.regression = sm.OLS(endog=y, exog=x).fit()

        # Find outliers #
        test = self.regression.outlier_test()
        outliers = (x[i] for i, t in enumerate(test) if t[2] < 0.5)
        print(f'R2={self.regression.rsquared}')
        list_outliers = list(outliers)
        print('Outliers at x= ', list_outliers)
        if list_outliers:
            self.linear_calibration(outliers=list_outliers, to_file=to_file)
        else:
            self._save_calibration(to_file)
            return self.regression

    def _save_calibration(self, to_file):
        params = self.regression.params
        conf_inter_param = self.regression.conf_int()
        dict_params = {"slope": params[0], "conf_interval": list(conf_inter_param[0])}

        with open(to_file, 'w') as fp:
            json.dump(dict_params, fp, indent=4, sort_keys=True)

    def plot_calibration(self):
        x = np.array(self.calibration_df["sample"].values)
        y = np.array(self.calibration_df["volume"].values)

        xnew = np.linspace(min(x), max(x), 1000)
        ynew = self.regression.predict(xnew)

        fig, ax = plt.subplots()
        ax.plot(x, y, 'o', label='experimental')
        ax.plot(xnew, ynew, label='linear model')

        conf_inter_param = self.regression.conf_int()

        ax.fill_between(xnew, xnew * conf_inter_param[0][0], xnew * conf_inter_param[0][1], label='Conf. Interv.',
                        alpha=0.3)

        ax.legend()
        ax.set_xlabel('Mass, mg')
        ax.set_ylabel('Blob volume, -')

        plt.show()
