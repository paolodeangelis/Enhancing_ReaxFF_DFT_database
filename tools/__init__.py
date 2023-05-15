"""
Handling AMSJob simulations and the ASE SQLite3 database.

This package provides functions for working with AMSJob objects from the SCM PLAMS library and store it in the
ASE SQLite3 database ase ASE AtomsRow objects.

TODO change

Note: The functions in this package require the SCM PLAMS library (version 1.5.1), ASE library and
the ADFSuite package to be installed.

Modules:
- `store_job`: Module containing functions for adding job information to the database.

Usage:
- Import the `add_to_db` function from this package to store job information in a database.

Example:
    from tools.db import add_to_db

    # Usage of the add_to_db function to store the job into a database.

Module Name: tools
Authors: Paolo De Angelis (paolo.deangelis@polito.it)
Copyright (c) 2023 Paolo De Angelis
"""
