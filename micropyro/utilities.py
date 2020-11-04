import json
import re

import pkg_resources


def get_atom_mw_dict():
    """
    This returns a dict with the atoms and their molecular weight.
    Reads from the database located in databases/atom_properties.json

    Returns
    ----------
    dict_atoms_mw: dict
        dictionary with atoms and mw: {'c':12, "h":1, etc}
    """
    atom_properties_data = pkg_resources.resource_filename('micropyro', 'databases/atom_properties.json')

    with open(atom_properties_data, 'r') as fp:
        dict_atoms_mw = json.load(fp)

    return dict_atoms_mw


def reader_json_totals(list_filenames):
    """
    This reads the json files with totals and returns them as a list of dicts.
    It will verify that the name of the file starts with totals.json to read it.
    This way, we can just send to the function all the files in the directory and it will take care
    of selecting the appropriate.

    Returns
    ----------
    list_totals_dict: list dicts
        list of dictionaries with the totals
    """
    list_totals_dict = []

    for file in list_filenames:
        # if it is a json results file, we process it.
        if "totals.json" in file:
            with open(file, 'r') as fp:
                data = json.load(fp)

            try:
                data['1st_react_temp'] = float(re.findall(r"(\d+)C", file)[0])
            except IndexError:
                pass
            try:
                data['2nd_react_temp'] = float(re.findall(r"(\d+)C", file)[2])
            except IndexError:
                pass
            try:
                data['mass ug'] = float(re.findall(r"(\d+) ug", file)[0])
            except IndexError:
                pass

            list_totals_dict.append(data)

    return list_totals_dict
