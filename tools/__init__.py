"""
Enhancing ReaxFF Database Tools.

This package provides functions for handling AMSJob simulations from the SCM PLAMS library
and storing the results in the ASE SQLite3 database as ASE AtomsRow objects.

Note: The functions in this package require the following dependencies to be installed:
SCM PLAMS library (version 1.5.1), ASE library, and ADFSuite package.

Modules:
- `db`: Contains functions for adding, retrieving, and analyzing simulation data in the database.
- `plams_experimental`: Provides functions for interacting with the SCM PLAMS library
using ASE calculators.

Package Name: tools
Authors: Paolo De Angelis (paolo.deangelis@polito.it)
Copyright (c) 2023 Paolo De Angelis
"""
