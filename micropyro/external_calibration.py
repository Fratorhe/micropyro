import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm


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
    remove_incomplete(self)
        remove incomplete points in the dataset
    linear_calibration(self, outliers=[], to_file="calibration.json", recursive=True)
        perform linear regression on the data.
    plot_calibration(self, save_plot=None)
        plot the calibration dataset, the regression and the uncertainties.
    drop_point(self, index_name)
        Method to drop points, barely used.
    _save_calibration(self, to_file)
        save to a json file
    """

    def __init__(self, calibration_df):
        """
        Defines the dataframe of the experiments.
        Sets all the characters to lower case to avoid duplicity or mismatches with database.

        Params
        -------
        calibration_df: dataframe with the appropriate columns (see examples)
        used_is: bool internal standard used or not.
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
        # get the indeces names before, in order to check which ones we do not include
        index_names_before = set(self.calibration_df.index.values.tolist())
        # drop the ones that the volume is not written or something.
        self.calibration_df = self.calibration_df[self.calibration_df['volume'].notna()]
        # save the index names after
        index_names_after = set(self.calibration_df.index.values.tolist())

        # print the ones removed.
        index_removed = index_names_before - index_names_after
        print(f"The following cases are removed because they are incomplete:")
        print(*index_removed, sep="\n")

        # return the indeces removed, in case you want to check them.
        return index_removed

    def linear_calibration(self, outliers=[], to_file="calibration.json", recursive=True):
        """
        Performs a linear calibration of the type y = a*x between the sample mass and the volume from GC Image.
        It is a recursive function which deletes outliers at every step. The recursivity can be controlled setting the
        recursive parameter to False.

        Parameters
        -----------
        recursive: bool
                Sets the recursivity of the function.
        outliers: list
                of outliers found after each iteration of the calibration.
        to_file: str
                Filename of the output of the calibration file.

        Returns
        --------
        self.regression: statmodel object
                With the results of the linear calibration
        """

        # get the x and y values (sample mass and volume from GC image)
        x = np.array(self.calibration_df["sample"].values)
        y = np.array(self.calibration_df["volume"].values)

        # if the outliers list contains any outlier (x value) we remove it from the lists
        for outlier in outliers:
            index = np.argwhere(x == outlier)
            x = np.delete(x, index)
            y = np.delete(y, index)

        # perform the linear regression using statmodels
        self.regression = sm.OLS(endog=y, exog=x).fit()

        # Find outliers (from stackoverflow: https://stackoverflow.com/questions/10231206/can-scipy-stats-identify-and-mask-obvious-outliers)
        test = self.regression.outlier_test()
        outliers = (x[i] for i, t in enumerate(test) if t[2] < 0.5)
        print(f'R2={self.regression.rsquared}')
        list_outliers = list(outliers)
        print('Outliers at x= ', list_outliers)

        # if there are outliers and the function is set to be recursive, we call it again
        if list_outliers and recursive:
            self.linear_calibration(outliers=list_outliers, to_file=to_file, recursive=recursive)
        else:
            # otherwise we just save it to the file, and keep on.
            self._save_calibration(to_file)
            return self.regression

    def _save_calibration(self, to_file):
        """
        Saves the calibration to a json file

        Parameters
        -----------
        to_file: str
                Filename of the file to be saved
        """
        params = self.regression.params
        conf_inter_param = self.regression.conf_int()
        dict_params = {"slope": params[0], "conf_interval": list(conf_inter_param[0])}

        with open(to_file, 'w') as fp:
            json.dump(dict_params, fp, indent=4, sort_keys=True)

    def plot_calibration(self, save_plot=None):
        """
        Plots the calibration. If save_plot is a filename, it will save it, otherwise, it will show it.

        :param save_plot: str
                Filename of the plot to be saved.
        """
        # get the x and y values (sample mass and volume from GC image) to make it easier
        x = np.array(self.calibration_df["sample"].values)
        y = np.array(self.calibration_df["volume"].values)

        # create a new space for plotting
        xnew = np.linspace(min(x)*0.99, max(x)*1.01, 1000)
        # use the regression to predict (y = a*x)
        ynew = self.regression.predict(xnew)

        # compute the confidence intervals
        conf_inter_param = self.regression.conf_int()

        ## plotting part
        fig, ax = plt.subplots()
        ax.plot(x, y, 'o', label='experimental')
        ax.plot(xnew, ynew, label='linear model')

        # draw the confidence intervals using a fill between with transparency
        ax.fill_between(xnew, xnew * conf_inter_param[0][0], xnew * conf_inter_param[0][1], label='Conf. Interv.',
                        alpha=0.3)

        # write the equation in the graph
        ax.annotate(f'vol = {self.regression.params[0]:.2f} mass', xy=(0.02, 0.65), xycoords='axes fraction')
        ax.annotate(f'R$^2$ = {self.regression.rsquared:.4f}', xy=(0.02, 0.55), xycoords='axes fraction')

        # put the legend and axis.
        ax.legend(loc="upper left")
        ax.set_xlabel('Mass, mg')
        ax.set_ylabel('Blob volume, -')

        # if you save in a file, I won't show it.
        if save_plot:
            fig.savefig(save_plot)
        else:
            plt.show()
