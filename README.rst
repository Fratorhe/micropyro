=========
micropyro
=========

.. image:: https://img.shields.io/travis/fratorhe/micropyro.svg
        :target: https://travis-ci.org/fratorhe/micropyro

.. image:: https://img.shields.io/pypi/v/micropyro.svg
        :target: https://pypi.python.org/pypi/micropyro


Package to analyse micropyrolysis data from GC Image software

* Free software: 3-clause BSD license
* Documentation: (Partly) https://fratorhe.github.io/micropyro.

Features
--------

* Read database of compounds.
* Read experimental matrix.
* Read blob files from GC Image.
* Compute yields based on the previous.

To Do
--------

* include gas and char yields
* mass balance
* elemental balance
* etc.

Install
--------

Clone the repository and install in developer mode with the following:

.. code-block:: shell-session

    $ git clone https://github.com/Fratorhe/micropyro
    $ cd micropyro
    $ pip install -e .