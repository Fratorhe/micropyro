import time

from bs4 import BeautifulSoup
import pubchempy as pcp
import urllib.request
import selenium.webdriver as webdriver
import selenium.common.exceptions as selenium_exceptions
import re
import statistics
from selenium.webdriver.firefox.options import Options


# class WebDriver:
#     # small class to use the with statement context manager
#     def __init__(self, driver):
#         self.driver = driver
#
#     def __enter__(self):
#         return self.driver
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.driver.quit()


class PubchemScrapper:
    # Scrapper for PubChem generic. First search the compound with the name to obtain the cid
    def __init__(self, smiles):
        # get the CID from the smiles
        cid = self.get_cid_from_smiles(smiles)
        # init for the compound and get the first cid (normally the one you are looking for)
        self.cid = cid
        self.compound = self.get_compound_from_cid(cid)
        # self.compound_found = self.get_compound_from_cid(self.cid)
        self.mol_weight = pcp.Compound.from_cid(self.cid).molecular_weight
        self.mol_formula = pcp.Compound.from_cid(self.cid).molecular_formula

    @classmethod
    def from_compound(cls, compound):
        cid = cls.get_cid(compound)
        return cls(cid)

    # @classmethod
    # def from_cid(cls, cid):
    #     compound = cls.get_compound_from_cid(cid)
    #     return cls(compound)

    @staticmethod
    def get_cid(compound):
        # gets the cid of a compound given the name.
        # Only retrieves the first cid.
        cids = pcp.get_cids(compound, 'name', 'substance')
        try:
            cid = cids[0]['CID'][0]
        except IndexError:
            cid = None
        return cid

    @staticmethod
    def get_compound_from_cid(cid):
        A = pcp.Compound.from_cid(cid=cid).iupac_name
        print(A)
        return A

    @staticmethod
    def get_cid_from_smiles(smiles):
        A = pcp.get_compounds(smiles, 'smiles')[0].cid
        print(A)
        return A

class PubchemGetProperty(PubchemScrapper):
    # Class to search for a property
    def __init__(self, smiles, property_to_search):
        super().__init__(smiles=smiles)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.tabs.warnOnClose", False)
        options = Options()
        options.add_argument('--headless') # this option allows to call firefox silently
        self.browser = webdriver.Firefox(firefox_profile=profile, options=options)

        if not self.cid:
            self.compound_or_property_found()

        self.property_to_search = property_to_search
        self.url = self.build_url()
        self.data = self.get_content_item()

    def build_url(self):
        url = 'https://pubchem.ncbi.nlm.nih.gov/compound/' + str(self.cid) + '#section=' + self.property_to_search + '&fullscreen=true'
        return url

    def get_content_item(self):
        self.browser.get(self.url)
        time.sleep(1) # give a bit of time to allow to load the website
        try:
            data = self.browser.find_element_by_id(self.property_to_search).find_elements_by_class_name('section-content-item')
        except selenium_exceptions.NoSuchElementException:
            data = None
            # self.compound_or_property_found()
        return data

    def compute_avg_std_property(self, property_list):
        if len(property_list) == 1:
            mean = property_list[0]
            std  = 0
        elif len(property_list) == 0:
            mean = "-1"
            std  = "-1"
        else:
            mean = statistics.mean(property_list)
            std  = statistics.stdev(property_list)

        return mean, std

    def __del__(self):
        print('closing connection to browser')
        try:
            self.browser.quit()
        except AttributeError:
            pass

    def compound_or_property_found(self):
        self.cid = None
        self.compound = None
        raise ValueError

class PubchemGetBoilingPoint(PubchemGetProperty):
    # Class to search for boiling point. Includes functions to transform temperatures etc.
    def __init__(self, smiles):
        property_to_search = 'Boiling-Point'
        super().__init__(smiles=smiles, property_to_search=property_to_search)
        self.temperature_units = {'C': self.from_C_to_K, 'F': self.from_F_to_K} # dictionary pointing to functions, avoid if-else
        if self.data is not None:
            self.temperatures_K = self.extract_temperatures()
            self.avg_boil_temp, self.std_boil_temp = self.compute_avg_std_property(self.temperatures_K)
        else:
            self.avg_boil_temp, self.std_boil_temp = ('','')

    def __str__(self):
        return "Boiling Point for %s: %s K, std %s" % (self.compound,self.avg_boil_temp, self.std_boil_temp)

    def extract_temperatures(self):
        temperatures = []
        units = []
        pattern = r'([+-]?\d+(\.\d+)*)\s?°([CcFf])'
        temperatures_K = []
        for reference_data in self.data:
            temperature = re.findall(pattern, reference_data.text)
            if temperature:
                temperatures.append(float(temperature[0][0]))
                units.append(temperature[0][2])

        for temperature, unit in zip(temperatures,units):
            temperature_K = self.temperature_units[unit](temperature) # applies the conversion from the dictionary
            temperatures_K.append(temperature_K)
        return temperatures_K

    def from_C_to_K(self,temperature_C):
        temperature_K = temperature_C+273.15
        return temperature_K

    def from_F_to_K(self, temperature_F):
        temperature_C = 5/9 * (temperature_F - 32)
        temperature_K = self.from_C_to_K(temperature_C)
        return temperature_K

# Example of use
# data_phenol = PubchemGetBoilingPoint('phenol')
# print(data_phenol.avg_boil_temp)