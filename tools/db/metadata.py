"""
Handling and updateing metadata of the ASE-SQLite3 database.

This package provides functions for working with the metadata of the ASE-SQLite3 database.

Package Name: metadata
Authors: Paolo De Angelis (paolo.deangelis@polito.it)
Copyright (c) 2023 Paolo De Angelis
"""
import json
import os

import numpy as np
import yaml
from ase.db.sqlite import SQLite3Database
from colorama import Fore, Style

INFO_SETS = {
    "description": "a short description for the",
    "unit": "the unit (if any) for the",
    "values": "the list of the values or the descriptio for the",
    "type": "the variable type (e.g. int, float, numpy.NDarray[float], etc.) for the",
}

INFP_USERS = {"name": "", "surname": "", "email": "", "institution": "", "country": ""}


def get_json_metadata(path: str, encoding: str = "utf-8") -> dict:
    """Get the metadata from a JSON file.

    Parameters:
        path (str): The path to the JSON file.
        encoding (str, optional): The encoding of the file (default is "utf-8").

    Returns:
        dict: The loaded metadata as a dictionary.
    """
    with open(path, encoding=encoding) as file:
        m_json = json.load(file)
    return m_json


def get_yaml_metadata(path: str, encoding: str = "utf-8") -> dict:
    """Get the metadata from a YAML file.

    Parameters:
        path (str): The path to the YAML file.
        encoding (str, optional): The encoding of the file (default is "utf-8").

    Returns:
        dict: The loaded metadata as a dictionary.
    """
    with open(path, encoding=encoding) as file:
        m_yaml = yaml.load(file, Loader=yaml.CFullLoader)
    return m_yaml


def write_json_metadata(path: str, metadata: dict, encoding: str = "utf-8") -> None:
    """Write the given metadata to a JSON file.

    Parameters:
        path (str): The path to the JSON file.
        metadata (dict): The metadata to be written.
        encoding (str, optional): The encoding of the file (default is "utf-8").
    """
    with open(path, "w", encoding=encoding) as file:
        json.dump(metadata, file, indent=4, sort_keys=False)


def write_yaml_metadata(path: str, metadata: dict, encoding: str = "utf-8") -> None:
    """Write the given metadata to a YAML file.

    Parameters:
        path (str): The path to the YAML file.
        metadata (dict): The metadata to be written.
        encoding (str, optional): The encoding of the file (default is "utf-8").
    """
    with open(path, "w", encoding=encoding) as file:
        yaml.dump(
            metadata,
            file,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=4,
            width=120,
            canonical=False,
        )


def message(msg: str, verbose: bool, msg_type="msg", **kwarg) -> None:
    """Print a message.

    Print the provided message if the `verbose` flag is set to True.

    Parameters:
        msg (str): The message to be printed.
        verbose (bool): Flag indicating whether to print the message or not.
        msg_type (str, optional): Type of the message (default is "msg").
            Possible values for `msg_type` are:
                - "msg": Regular message (default).
                - "info": Informational message.
                - "warning": Warning message.
                - "error": Error message.
        **kwarg: Additional keyword arguments for the print function.
    """
    if verbose:
        if msg_type == "info":
            print(Fore.BLUE + msg + Style.RESET_ALL, **kwarg)
        elif msg_type == "warning":
            print(Fore.YELLOW + msg + Style.RESET_ALL, **kwarg)
        elif msg_type == "error":
            print(Fore.RED + msg + Style.RESET_ALL, **kwarg)
        else:
            print(msg, **kwarg)


def get_unique_values(db: SQLite3Database, key: str) -> list:
    """Get unique values for a given key from a database.

    This function retrieves unique values for the specified key from a database.
    It iterates over the rows in the database and collects the values associated with the key.
    Duplicate values are removed, and the unique values are returned as a list.

    Parameters:
        db (SQLite3Database): The database to retrieve values from.
        key (str): The key to extract values for.

    Returns:
        list: A list of unique values for the specified key in the database.
    """
    subset_name = []
    n_row = db.count()
    for row in db.select(f"id<{n_row*10}"):
        try:
            subset_name.append(row[key])
        except AttributeError:
            pass
    return np.unique(subset_name).tolist()


def get_new_values_in_key(metadata: dict, key: str, values: list[str]) -> list:
    """Get the new values in a key.

    This function retrieves the new values in a key from the metadata.
    It compares the values in the key with the values provided in the `values` argument.
    The new values are returned asa list.

    Parameters:
        metadata (dict): The metadata to retrieve the new values from.
        key (str): The key to retrieve the new values from.
        values (list[str]): The values to compare with the values in the key.

    Returns:
        list: A list of new values in the key.
    """
    new_values = []
    old_metadata = metadata["keys"][key]["values"].keys()
    for value in values:
        if value not in old_metadata:
            new_values.append(value)
    return new_values


def update_new_values_in_key(metadata: dict, key: str, new_values: list[str]) -> dict:
    """Update the metadata with new values for a given key.

    This function updates the metadata by adding new values for the specified key.
    It prompts the user to provide additional information for each new value based on the key type.
    The updated metadata is returned.

    Parameters:
        metadata (dict): The existing metadata.
        key (str): The key to update with new values.
        new_values (list[str]): A list of new values to be added to the metadata.

    Raises:
        ValueError: If a mandatory description is not provided for the key.
        NotImplementedError: If the update for the `key` is not implemented yet.

    Example:
        >>> metadata = {
        ...     "keys": {
        ...         "user": {
        ...             "values": {
        ...                 "user 1": {
        ...                     "name": "User",
        ...                     "surname": "One",
        ...                     "email": "uset@polito.it",
        ...                     "institution": "Politecnico di Torino",
        ...                     "country": "Italy"
        ...                 }
        ...             }
        ...         }
        ...     }
        ... }
        >>> new_users = ["user 2"]
        >>> updated_metadata = update_new_values_in_key(metadata, "user", new_users)
        == Updating the metadata for the new values in key 'user' =========================================
        Please add the name of `user 2`
             `user 2` name [None]: User
        Please add the surname of `user 2`
             `user 2` surname [None]: Two
        Please add the email of `user 2`
             `user 2` email [None]: user2@polito.it
        Please add the institution of `user 2`
             `user 2` institution [None]: Politecnico di Torino
        Please add the country of `user 2`
             `user 2` country [None]: Italy
        -- Thanks for your input! ----------------------------------------------------------------------------

    Returns:
        dict: The updated metadata after adding the new values.
    """
    new_metadata = metadata.copy()
    message(
        f"== Updating the metadata for the new values in key `{key}` ".ljust(80, "="),
        True,
        msg_type="msg",
        end="\n",
    )
    if key == "user":
        info_keys = INFP_USERS.keys()
        for value in new_values:
            new_metadata["keys"][key]["values"][value] = {}
            for info_key in info_keys:
                message(
                    f"Please add the {info_key} of `{value}`  ",
                    True,
                    msg_type="msg",
                    end="\n",
                )
                user_input = input(f"\t `{value}`{info_key} [None]:")
                if user_input == "":
                    new_metadata["keys"][key]["values"][value][info_key] = None
                else:
                    new_metadata["keys"][key]["values"][value][info_key] = user_input
    elif key == "subset_name":
        for value in new_values:
            message(
                "Please add the description of the new subset of simulation",
                True,
                msg_type="msg",
                end="\n",
            )
            user_input = input(f"\t `{value}` description:")
            if user_input == "":
                raise ValueError("A description is mandatory")
            else:
                new_metadata["keys"][key]["values"][value] = user_input
    elif key == "task":
        for value in new_values:
            message(
                "Please add the description of the new task of simulation",
                True,
                msg_type="msg",
                end="\n",
            )
            user_input = input(f"\t `{value}` description [None]:")
            if user_input == "":
                new_metadata["keys"][key]["values"][value] = None
            else:
                new_metadata["keys"][key]["values"][value] = user_input
    elif key == "used_in":
        for value in new_values:
            message(
                "Please add the description of the new subset in `used_in`",
                True,
                msg_type="msg",
                end="\n",
            )
            user_input = input(f"\t `{value}` description:")
            if user_input == "":
                raise ValueError("A description is mandatory")
            else:
                new_metadata["keys"][key]["values"][value] = user_input
    elif key == "else":
        raise NotImplementedError("The update for this key is not implemented yet")
    message("-- Thanks for your input! ".ljust(80, "-"), True, msg_type="msg", end="\n")
    return new_metadata


def update_metadata(db: SQLite3Database, verbose: bool = True) -> None:
    """Update the metadata for a database.

    This function updates the metadata for a database by checking and adding new values
    for specific keys: 'user', 'subset_name', 'task', and 'used_in'. It loads the existing
    metadata, checks for new values in each key, prompts the user for additional information
    if necessary, and saves the updated metadata.

    Parameters:
        db (SQLite3Database): The SQLite database object.
        verbose (bool, optional): Whether to display detailed messages. Defaults to True.

    Raises:
        ValueError: If a mandatory description is not provided for the key.
        NotImplementedError: If the update for the specific `key` is not implemented yet.

    Example:
        >>> db = ase.db.connect('data/LiF.db)
        >>> update_metadata(db)
        Metadata loaded
        No new values in key 'user'
        New values in key 'subset_name': ['subset3', 'subset4']
        == Updating the metadata for the new values in key 'subset_name' =========================================
        Please add the description of the new subset of simulation
            'subset3' description:Subset 3 description
        Please add the description of the new subset of simulation
            'subset4' description:Subset 4 description
        -- Thanks for your input! -----------------------------------------------------------------------------
        Metadata saved
        No new values in key 'task'
        No new values in key 'used_in'
        Metadata saved

    Returns:
        None
    """
    db_folder = os.path.dirname(db.filename)
    db_name = os.path.split(db.filename)[1].split(".")[0]
    message("Loading metadata...", verbose, msg_type="info", end="\r")
    metadata = get_json_metadata(os.path.join(db_folder, db_name + ".json"))
    message("Metadata loaded     ", verbose, msg_type="info", end="\n")
    # metadata_yaml = get_yaml_metadata( os.path.join(db_folder, db_name + '.yaml') )
    metadata_new = metadata.copy()
    for key in ["user", "subset_name", "task", "used_in"]:
        updated = False
        message(f"Check `{key}` values..", verbose, msg_type="info", end="\r")
        values = get_unique_values(db, key)
        new_values = get_new_values_in_key(metadata, key, values)
        if len(new_values) > 0:
            message(
                f"New values in key `{key}`: {new_values}",
                True,
                msg_type="warning",
                end="\n",
            )
            metadata_new = update_new_values_in_key(metadata_new, key, new_values)
            updated = True
        else:
            message(f"No new values in key `{key}`", verbose, msg_type="info", end="\n")
        if updated:
            message("Saving  metadata...", verbose, msg_type="info", end="\r")
            write_json_metadata(
                os.path.join(db_folder, db_name + ".json"), metadata_new
            )
            write_yaml_metadata(
                os.path.join(db_folder, db_name + ".yaml"), metadata_new
            )
            message("Metadata saved     ", verbose, msg_type="info", end="\n")
    metadata_new["rows"] = db.count()
    message("Saving  metadata...", verbose, msg_type="info", end="\r")
    write_json_metadata(os.path.join(db_folder, db_name + ".json"), metadata_new)
    write_yaml_metadata(os.path.join(db_folder, db_name + ".yaml"), metadata_new)
    message("Metadata saved     ", verbose, msg_type="info", end="\n")
    return None
