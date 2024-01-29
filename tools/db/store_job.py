"""
Store AMSJob simulations into ASE SQLite3 database.

This package provides functions for working with AMSJob objects from the SCM PLAMS library and store it in the
ASE SQLite3 database.

Note: The functions in this package require the SCM PLAMS library (version 1.5.1), ASE library and
the ADFSuite package to be installed.

Package Name: store_job
Authors: Paolo De Angelis (paolo.deangelis@polito.it)
Copyright (c) 2023 Paolo De Angelis
"""

import datetime as dt
import os
import re
from datetime import datetime
from typing import Any, Literal, Union

import ase
import numpy as np
from ase import Atoms
from ase.db.row import AtomsRow
from ase.db.sqlite import SQLite3Database
from numpy import ndarray
from scm.plams import AMSJob
from scm.plams.interfaces.molecule.ase import toASE as SCMtoASE
from scm.plams.tools.units import Units

from ..plams_experimental.ase_calculator import AMSCalculator

# Please note that the above line of code assumes that you have installed the SCM PLAMS library (version 1.5.1)
# and the ADFSuite package. the `AMSCalculator` is not yet released in the PLASM library.
# once the AMSCalculator class is released in the PLAMS library, you can use this line of code to import it.
# from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator


def get_runtime(job: AMSJob) -> Union[datetime, Literal["Not Started"]]:
    """Get the runtime of a job.

    Args:
        job (AMSJob): The AMS job object that handle the simulation.

    Returns:
        Union[dt.datetime, Literal['Not Started']]: The runtime of the job as a datetime object
            or the string 'Not Started' if the log file is not found.

    Raises:
        None.

    Example:
        >>> job = AMSJob(...)
        >>> job.run()
        >>> get_runtime(job)
        datetime.datetime(2023, 1, 1, 10, 30, 0)
    """
    try:
        ams_log = os.path.join(job.path, "ams.log")
        with open(ams_log) as file:
            line = file.readline()
        match = re.search(r"[A-Z][a-z][a-z]\d\d-\d\d\d\d \d\d:\d\d:\d\d", line)
        if match is not None:
            runtime = dt.datetime.strptime(str(match.group()), r"%b%d-%Y %H:%M:%S")
        else:
            runtime = "Not Started"  # type: ignore
    except FileNotFoundError:
        runtime = "Not Started"  # type: ignore
    return runtime


def get_input_atoms_from_ams(job: AMSJob) -> Atoms:
    """Retrieve the input atoms object from an AMSJob.

    This function extracts the input molecular structure from an AMSJob object and converts it
    into an ASE Atoms object.

    Args:
        job (AMSJob): An instance of the AMSJob class representing the job.

    Returns:
        Atoms: The molecular structure as an ASE Atoms object.

    Raises:
        None.

    Example:
        >>> job = AMSJob(...)
        >>> atoms = get_input_atoms_from_ams(job)
        >>> atoms
        Atoms(symbols='LiF', pbc=False)
    """
    molecule = job.results.get_input_molecule()
    atoms = SCMtoASE(molecule)
    return atoms


def get_atoms_from_ams(job: AMSJob) -> Atoms:
    """Retrieve the atoms object with calculation data from an AMSJob.

    This function extracts the molecular structure, sets up an ASE Atoms object, attaches an
    AMSCalculator to it, and add to the calculator the results and settings from the
    AMSJob.

    Args:
        job (AMSJob): An instance of the AMSJob class representing the job.

    Returns:
        Atoms: The molecular structure with attached AMSCalculator and populated with
            calculation results and settings.

    Raises:
        None.

    Example:
        >>> job = AMSJob(...)
        >>> job.run()
        >>> atoms = get_atoms_from_ams(job)
        >>> atoms
        Atoms(symbols='H2O', pbc=True, calculator=AMSCalculator(...))
    """
    molecule = job.results.get_molecule("Molecule")
    atoms = SCMtoASE(molecule)
    calc = AMSCalculator(settings=job.settings, restart=False, molecule=molecule)
    atoms.calc = calc
    atoms.calc.results_from_ams_results(job.results, job.settings)
    return atoms


def get_space_group(job: AMSJob) -> Union[str, None]:
    """Extract the Full International Space Group symbol from the given job name.

    Args:
        job (AMSJob): The AMSJob object representing the job.

    Returns:
        Union[str, None]: Full International Space Group symbol if found, None otherwise.
            The notation is a LaTeX-like string, with screw axes being represented by an underscore.
            See pymatgen.symmetry.groups module for more dettails.

    Example:
        >>> job = AMSJob(...)
        >>> job.name = "GO-1.0-2-LiF_Pm-3m_-2.89_2x1x1"
        >>> get_space_group(job)
        'Pm-3m'
    """
    search = re.search(r"(?<=LiF_)\w+?\S\w+(?=_-\d_?)", job.name)
    if search is None:
        search = re.search(r"(?<=F_)\w+?\S\w+(?=_-?\d)", job.name)
    if search is None:
        search = re.search(r"(?<=Li_)\w+?\S\w+(?=_-?\d)", job.name)
    if search is not None:
        spgroup = search.group()
    else:
        spgroup = None
    return spgroup


def get_band_info(job: AMSJob) -> tuple[float, float, float, float]:
    """Get the band structure information from an AMS BAND simulation.

    Args:
        job (AMSJob): An AMSJob object containing the result from BAND simulation.

    Returns:
        Tuple[float, float, float, float]: A tuple containing the following electronic band information:
            - fermi_energy (float): The Fermi energy in electron volts (eV).
            - homo_energy (float): The energy of the highest occupied molecular orbital (HOMO) in electron volts (eV).
            - lumo_energy (float): The energy of the lowest unoccupied molecular orbital (LUMO) in electron volts (eV).
            - band_gap (float): The band gap energy in electron volts (eV).

    Example:
        >>> job = AMSJob(...)
        >>> job.run()
        >>> fermi_energy, homo_energy, lumo_energy, band_gap = get_band_info(job)
        >>> print(f"Fermi energy: {fermi_energy} eV")
        Fermi energy: -7.524870077626501 eV
        >>> print(f"HOMO energy: {homo_energy} eV")
        HOMO energy: -4.814847514947701 eV
        >>> print(f"LUMO energy: {lumo_energy} eV")
        LUMO energy: -13.571829692390196 eV
        >>> print(f"Band gap: {band_gap} eV")
        Band gap: 8.756982177442497 eV
    """
    band_structure_data = job.results.read_rkf_section("BandStructure", file="band")
    fermi_energy = Units.convert(band_structure_data["FermiEnergy"], "au", "eV")
    band_gap = Units.convert(band_structure_data["BandGap"], "au", "eV")
    bandsenergy = Units.convert(band_structure_data["bandsEnergyRange"], "au", "eV")
    bandsenergy = np.sort(bandsenergy)
    homo_indx = np.where(bandsenergy < fermi_energy)[0][-1]
    lumo_energy = bandsenergy[homo_indx]
    homo_energy = bandsenergy[homo_indx + 1]
    return fermi_energy, homo_energy, lumo_energy, band_gap


def get_dos(job: AMSJob) -> dict[str, ndarray]:
    """Get the density of states (DOS) data from an AMSJob object.

    Args:
        job (AMSJob): An AMSJob object containing the simulation results.

    Returns:
        Dict[str, ndarray]: A dictionary containing the DOS data with the following keys:
            - "Energy [eV]": An ndarray of energy values in electron volts (eV).
            - "Total DOS [1/eV]": An ndarray of total DOS values in inverse electron volts (1/eV).

    Note:
        The function reads the DOS data from the specified section of the BAND .rkf file.
    """
    dos_data = job.results.read_rkf_section("DOS", file="band")
    k = Units.convert(1, "au", "eV")
    dos = {
        "Energy [eV]": np.array(dos_data["Energies"]) * k,
        "Total DOS [1/eV]": np.array(dos_data["Total DOS"]) / k,
    }
    return dos


def get_history(
    job: AMSJob,
) -> dict[str, ndarray]:
    """Retrieve and process historical data from an AMSJob object.

    Args:
        job (AMSJob): An AMSJob object containing the required historical data.

    Returns:
        Dict[str, ndarray]: A dictionary containing the simulation
            trajectory data with the following quontities (keys):
            - "Energy [eV]": An ndarray of energy values in electron volts (eV).
            - "Max force [eV/A]": An ndarray of maximum force values in electron
                                  volts per angstrom (eV/A).
            - "RMS force [eV/A]": An ndarray of root mean square force values in
                                  electron volts per angstrom (eV/A).
            - "Max step [A]": An ndarray of maximum step values in angstrom (A).
            - "RMS step [A]": An ndarray of root mean square step values in angstrom (A).
            - "Max stress per atom [eV/A^3]": An ndarray of maximum stress per atom values in
                                              electron volts per angstrom cubed (eV/A^3).
    """
    history_data = job.results.read_rkf_section("History", file="ams")
    try:
        nentries = history_data["nEntries"]
        energy = np.zeros(nentries)
        maxf = np.zeros(nentries)
        rmsf = np.zeros(nentries)
        maxstep = np.zeros(nentries)
        rmsstep = np.zeros(nentries)
        maxstres = np.zeros(nentries)
        for i in range(nentries):
            energy[i] = Units.convert(history_data[f"Energy({i+1:d})"], "au", "eV")
            maxf[i] = Units.convert(history_data[f"maxGrad({i+1:d})"], "hartree/bohr", "eV/angstrom")
            rmsf[i] = Units.convert(history_data[f"rmsGrad({i+1:d})"], "hartree/bohr", "eV/angstrom")
            maxstep[i] = Units.convert(history_data[f"maxStep({i+1:d})"], "bohr", "A")
            rmsstep[i] = Units.convert(history_data[f"rmsStep({i+1:d})"], "bohr", "A")
            maxstres[i] = Units.convert(
                history_data[f"MaxStressEnergyPerAtom({i+1:d})"],
                "hartree/bohr^3",
                "eV/angstrom^3",
            )
    except KeyError:
        energy, maxf, rmsf, maxstep, rmsstep, maxstres = [None] * 6
    history = {
        "Energy [eV]": energy,
        "Max force [eV/A]": maxf,
        "RMS force [eV/A]": rmsf,
        "Max step [A]": maxstep,
        "RMS step [A]": rmsstep,
        "Max stress per atom [eV/A^3]": maxstres,
    }
    return history


def is_in_trainigset(job: AMSJob, fulldataset_path: str, trainigset_path: str) -> str:
    """Check if a given job is present in the training or test dataset.

    Args:
        job (AMSJob): An AMSJob object of the job to be checked.
        fulldataset_path (str): The file path to the full dataset file.
        trainigset_path (str): The file path to the training dataset file.

    Returns:
        str: A string indicating the usage of the job:
            - "training" if the job is found in the training dataset.
            - "test" if the job is found in the test dataset.
            - "none" if the job is not found in either dataset.

    Note:
        The function reads the contents of the full dataset file and the training dataset file to perform the check.
        It compares the name of the given job with the dataset contents to determine its usage.
    """
    used_in = None
    with open(fulldataset_path) as file:
        fulldataset = "\n".join(file.readlines())
    with open(trainigset_path) as file:
        trainigset = "\n".join(file.readlines())

    if job.name in fulldataset:
        if job.name in trainigset:
            used_in = "training"
        else:
            used_in = "test"
    else:
        used_in = "none"
    return used_in


def get_key_value(row: AtomsRow, key: str) -> Union[Any, None]:
    """Get a value associated with a given key from a row object.

    Args:
        row (AtomsRow): A AtomsRow object from the database.
        key (str): The key of the value to be retrieved.

    Returns:
        Union[Any, None]: The value associated with the given key if it exists,
                          or None if the key is not found in the AtomsRow object.

    Note:
        The function attempts to retrieve the value associated with the given key from the AtomsRow object.
        If the key is found, the corresponding value is returned.
        If the key is not found or if the AtomsRow object does not support attribute-style access, None is returned.
    """
    try:
        return row[key]
    except AttributeError:
        return None


def row_info(row: AtomsRow) -> str:
    """Generate formatted information about an AtomsRow object.

    Args:
        row (AtomsRow): A AtomsRow object from the database containing information to be formatted.

    Returns:
        str: A string containing information about the row object.

    Note:
        The function generates a formatted representation of the AtomsRow object's data,
        including its id, user, name, task, formula, energy, success, and used_in properties.
        The information is presented in a table-like format with aligned columns.

    Example:
        >>> row = db.get("id=11")
        >>> row_info(row)
        id |      user      |       name       |       task       | formula |  energy  | success |  used_in
         1 | Paolo De Ange* | 0-LiF_Fm-3m_-3.* | initial configu* | LiF     |          |         |      none

    """
    heder = (
        f"\t  id | {'user'.center(14)} | {'name'.center(16)} | {'task'.center(16)} |"
        " formula |  energy  | success |  used_in  "
    )
    user = row.user
    if len(user) > 14:
        user = user[:13] + "*"
    task = row.task
    if len(task) > 16:
        task = task[:15] + "*"
    name = row.name
    if len(name) > 16:
        name = name[:15] + "*"
    success = get_key_value(row, "success")
    energy = get_key_value(row, "energy")
    used_in = get_key_value(row, "used_in")
    if energy is not None:
        energy = f"{energy:>8.3f}"
    else:
        energy = ""
    if success is not None:
        success = f"{success}"
    else:
        success = ""
    if used_in is None:
        used_in = ""

    data = (
        f"\t {row.id:>3d} | {user:<14s} | {name:<16s} | {task:<16s} | {row.formula:<7s} "
        f"| {energy:>8s} | {success:>7s} | {used_in:>9s} "
    )
    return "\n".join([heder, data])


def add_sim_to_db(
    db: SQLite3Database,
    job: AMSJob,
    subset_name: str,
    user: str,
    task: str,
    use_runtime: bool = True,
    fulldataset_path: Any | None = None,
    trainigset_path: Any | None = None,
) -> None:
    """Store the AMS simulation to the ASE SQLite3 database as ase.AtomsRow object.

    Args:
        db (SQLite3Database): The ASE SQLite3 database to add the information to.
        job (AMSJob): An AMSJob object containing the calculation results.
        subset_name (str): The name of the subset to which the job belongs.
        user (str): Data point author.
        task (str): The task name associated with the job.
        use_runtime (bool, optional): Whether to use the runtime information as cration
                                      time of the data in the database. Defaults to True.
        fulldataset_path (Any | None, optional): The path to the full dataset file. Defaults to None.
        trainigset_path (Any | None, optional): The path to the training set file. Defaults to None.

    Returns:
        None

    Note:
        The function adds AMS simulation information from the AMSJob object to the provided SQLite3 database.
        It extracts relevant information such as runtime, atoms, space group, band structure, functional,
        density of states (DOS), and history. The extracted data is then written to the database using the
        provided database object. Additionally, the function populates other relevant fields such as input
        script, run script, simulation name, success status, subset name, elapsed time, and more.

        If `use_runtime` is True, the function uses the runtime information from the job to set the `ctime`
        field in the database. Otherwise, the current time is used.

        If `fulldataset_path` or `trainigset_path` is provided, the function determines whether the job is
        used in the full dataset or training set by calling the `is_in_trainigset` function.

    Example:
        >>> db = ase.db.connect(os.path.join('data', "LiF.db")) # Create to the SQLite3 database object
        >>> job = AMSjob(...)
        >>> job.run()
        >>> add_sym_to_db(db, job, "unit cell", "single point", use_runtime=True,
        ...               fulldataset_path="fulldataset.yaml", trainigset_path="trainigset.yaml")
    """
    YEAR = 31557600.0
    atoms = get_atoms_from_ams(job)
    atoms_row = ase.db.row.AtomsRow(atoms)
    runtime = get_runtime(job)
    if isinstance(runtime, datetime):
        runtime_str = runtime.strftime("%a %d %b %Y, %H:%M:%S")
        if use_runtime:
            atoms_row.ctime = (runtime - dt.datetime(2000, 1, 1)).total_seconds() / YEAR  # time since January 1. 2000
        else:
            atoms_row.ctime = ase.db.core.now()
    else:
        runtime_str = runtime
        atoms_row.ctime = ase.db.core.now()
    if fulldataset_path and trainigset_path is not None:
        used_in = is_in_trainigset(job, fulldataset_path, trainigset_path)
    else:
        used_in = "none"
    atoms_row.user = user
    atoms_row.calculator = "/".join(["ams"] + job.results.engine_names())
    atoms_row.calculator_parameters = job.settings.as_dict()
    space_group = get_space_group(job)
    fermi_energy, homo_energy, lumo_energy, band_gap = get_band_info(job)
    functional_list = []
    for xc_type, name in job.settings["input"][job.results.engine_names()[0]]["xc"].items():
        functional_list.append(f"{xc_type}/{name}")
    functional = ", ".join(functional_list)
    # Additional data
    data = {}
    data["DOS"] = get_dos(job)
    data["History"] = get_history(job)
    name = "-".join(job.name.split("-")[1:])
    # Write
    db.write(
        atoms_row,
        input_script=job.get_input(),
        run_script=job.get_runscript(),
        sim_name=job.name,
        name=name,
        success=job.results.ok(),
        space_group=space_group,
        subset_name=subset_name,
        functional=functional,
        runtime=runtime_str,
        fermi_energy=fermi_energy,
        homo_energy=homo_energy,
        lumo_energy=lumo_energy,
        band_gap=band_gap,
        data=data,
        used_in=used_in,
        task=task,
        elapsed=job.results.get_timings()["elapsed"],
    )


def add_ic_to_db(db: SQLite3Database, job: AMSJob, subset_name: str, user: str, use_runtime: bool = True) -> None:
    """Add initial configuration ASE Atoms to the database from an AMSJob object.

    Args:
        db (SQLite3Database): The database object to add the information to.
        job (AMSJob): An AMSJob object containing the calculation results.
        subset_name (str): The name of the subset to which the job belongs.
        user (str): Data point author.
        use_runtime (bool): Whether to use the runtime information from the job. Defaults to True.

    Returns:
        None

    Example:
        >>> db = ase.db.connect(os.path.join('data', "LiF.db")) # Create to the SQLite3 database object
        >>> job = AMSjob(...)
        >>> job.run()
        >>> add_sym_to_db(db, job, "unit cell", use_runtime=True)
    """
    YEAR = 31557600.0
    atoms = get_input_atoms_from_ams(job)
    atoms_row = ase.db.row.AtomsRow(atoms)
    runtime = get_runtime(job)
    if isinstance(runtime, datetime):
        runtime_str = runtime.strftime("%a %d %b %Y, %H:%M:%S")
        if use_runtime:
            atoms_row.ctime = (runtime - dt.datetime(2000, 1, 1)).total_seconds() / YEAR  # time since January 1. 2000
        else:
            atoms_row.ctime = ase.db.core.now()
    else:
        runtime_str = runtime
        atoms_row.ctime = ase.db.core.now()
    used_in = "none"
    task = "initial configuration"
    atoms_row.user = user
    space_group = get_space_group(job)
    name = "-".join(job.name.split("-")[1:])
    # Write
    db.write(
        atoms_row,
        sim_name=job.name,
        name=name,
        space_group=space_group,
        subset_name=subset_name,
        runtime=runtime_str,
        used_in=used_in,
        task=task,
    )


def add_to_db(
    db: SQLite3Database,
    job: AMSJob,
    subset_name: str,
    task: str,
    user: str = None,  # type: ignore
    add_ic: bool = False,
    use_runtime: bool = True,
    fulldataset_path: Any | None = None,
    trainigset_path: Any | None = None,
    verbose: bool = True,
) -> None:
    """Add simulation and optional initial configuration information to a database for an AMSJob object.

    Args:
        db (SQLite3Database): The ASE SQLite3 database to add the information to.
        job (AMSJob): An AMSJob object containing the calculation results.
        subset_name (str): The name of the subset to which the job belongs.
        task (str): The task name associated with the job.
        user (str | None, optional): Data point author, if None it will use the value from
                                     the enviroment variable `USER`. Defaults to None.
        add_ic (bool, optional): Whether to add initial configuration information. Defaults to False.
        use_runtime (bool, optional): Whether to use the runtime information as cration
                                      time of the data in the database. Defaults to True.
        fulldataset_path (Any | None, optional): The path to the full dataset file. Defaults to None.
        trainigset_path (Any | None, optional): The path to the training set file. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to True.

    Returns:
        None

    Note:
        The function store the AMSjob simulation as ASE AtomsRow object into the provided database.
        It extracts relevant information such as runtime, space group, task, and other optional data
        associated with the job.

        If `add_ic` is set to True, the function also adds initial configuration information to the database
        using the `add_ic_to_db` function. The `use_runtime` parameter determines whether to use the runtime
        information from the job. If `verbose` is True, the function prints information about the added data.

    Example:
        >>> db = ase.db.connect(os.path.join('data', "LiF.db")) # Create to the SQLite3 database object
        >>> job = AMSjob(...)
        >>> job.run()
        >>> add_to_db(db, job, "unit cell", "single point", add_ic=True, use_runtime=True,
        ...               fulldataset_path="fulldataset.yaml", trainigset_path="trainigset.yaml")
        Added `single point` of simulation: /path/to/the/simulation_folder
            id |      user      |       name       |       task       | formula |  energy  | success |  used_in
             4 | Paolo De Ange* | 1-LiF_P6_3mc_-3* | single point     | Li2F2   |  -19.209 |    True |      none
    """
    if user is None:
        user = os.environ["USER"]
    if add_ic:
        add_ic_to_db(db, job, subset_name, user, use_runtime=use_runtime)
        if verbose:
            last_id = db.count()
            row = db.get(id=last_id)
            print(f"Added `{row.task}` of simulation: {job.path}")
            print(row_info(row))
    # Add simulation
    add_sim_to_db(
        db,
        job,
        subset_name,
        user,
        task,
        use_runtime=use_runtime,
        fulldataset_path=fulldataset_path,
        trainigset_path=trainigset_path,
    )
    if verbose:
        last_id = db.count()
        row = db.get(id=last_id)
        print(f"Added `{row.task}` of simulation: {job.path}")
        print(row_info(row))
