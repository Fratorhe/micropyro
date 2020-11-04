import json

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
