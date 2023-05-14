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
from typing import Literal, Union

import ase
import numpy as np
from ase import Atoms
from scm.plams import AMSJob
from scm.plams.interfaces.molecule.ase import toASE as SCMtoASE
from scm.plams.tools.units import Units

from ..plasm_experimental.ase_calculator import AMSCalculator

# Please note that the above line of code assumes that you have installed the SCM PLAMS library (version 1.5.1)
# and the ADFSuite package. the `AMSCalculator` is not yet released in the PLASM library.
# once the AMSCalculator class is released in the PLAMS library, you can use this line of code to import it.
# from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator


def get_runtime(job: AMSJob) -> Union[dt.datetime, Literal["Not Started"]]:
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
        runtime = re.search(
            r"[A-Z][a-z][a-z]\d\d-\d\d\d\d \d\d:\d\d:\d\d", line
        ).group()
        runtime = dt.datetime.strptime(runtime, r"%b%d-%Y %H:%M:%S")
    except FileNotFoundError:
        runtime = "Not Started"
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


def get_space_group(job):
    search = re.search(r"(?<=LiF_)\S+(?=_)", job.name)
    if search is None:
        search = re.search(r"(?<=F_)\S+(?=_)", job.name)
    if search is None:
        search = re.search(r"(?<=Li_)\S+(?=_)", job.name)
    return search.group()


def get_band_info(job):
    band_structure_data = job.results.read_rkf_section("BandStructure", file="band")
    fermi_energy = Units.convert(band_structure_data["FermiEnergy"], "au", "eV")
    band_gap = Units.convert(band_structure_data["BandGap"], "au", "eV")
    bandsenergy = Units.convert(band_structure_data["bandsEnergyRange"], "au", "eV")
    bandsenergy = np.sort(bandsenergy)
    homo_indx = np.where(bandsenergy < fermi_energy)[0][-1]
    lumo_energy = bandsenergy[homo_indx]
    homo_energy = bandsenergy[homo_indx + 1]
    return fermi_energy, homo_energy, lumo_energy, band_gap


def get_dos(job):
    dos_data = job.results.read_rkf_section("DOS", file="band")
    k = Units.convert(1, "au", "eV")
    dos = {
        "Energy [eV]": np.array(dos_data["Energies"]) * k,
        "Total DOS [1/eV]": np.array(dos_data["Total DOS"]) / k,
    }
    return dos


def get_history(job):
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
            maxf[i] = Units.convert(
                history_data[f"maxGrad({i+1:d})"], "hartree/bohr", "eV/angstrom"
            )
            rmsf[i] = Units.convert(
                history_data[f"rmsGrad({i+1:d})"], "hartree/bohr", "eV/angstrom"
            )
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


def is_in_trainigset(job, fulldataset_path, trainigset_path):
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


def get_key_value(row, key):
    try:
        return row[key]
    except AttributeError:
        return None


def row_info(row):
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


def add_sym_to_db(
    db,
    job,
    subset_name,
    task,
    use_runtime=True,
    fulldataset_path="last_attempt/training/dataset.yaml",
    trainigset_path="last_attempt/training/dataset_1over3.yaml",
):
    YEAR = 31557600.0
    runtime = get_runtime(job)
    try:
        runtime_str = runtime.strftime("%a %d %b %Y, %H:%M:%S")
    except AttributeError:
        runtime_str = runtime
    atoms = get_atoms_from_ams(job)
    used_in = is_in_trainigset(job, fulldataset_path, trainigset_path)
    atoms_row = ase.db.row.AtomsRow(atoms)
    atoms_row.user = "Paolo De Angelis"
    atoms_row.calculator = "/".join(["ams"] + job.results.engine_names())
    atoms_row.calculator_parameters = job.settings.as_dict()
    if use_runtime:
        atoms_row.ctime = (
            runtime - dt.datetime(2000, 1, 1)
        ).total_seconds() / YEAR  # time since January 1. 2000
    else:
        atoms_row.ctime = ase.db.core.now()
    space_group = get_space_group(job)
    fermi_energy, homo_energy, lumo_energy, band_gap = get_band_info(job)
    functional = []
    for xc_type, name in job.settings["input"][job.results.engine_names()[0]][
        "xc"
    ].items():
        functional.append(f"{xc_type}/{name}")
    functional = ", ".join(functional)
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


def add_ic_to_db(db, job, subset_name, use_runtime=True):
    YEAR = 31557600.0
    runtime = get_runtime(job)
    try:
        runtime_str = runtime.strftime("%a %d %b %Y, %H:%M:%S")
    except AttributeError:
        runtime_str = runtime
    atoms = get_input_atoms_from_ams(job)
    used_in = "none"
    task = "initial configuration"
    atoms_row = ase.db.row.AtomsRow(atoms)
    atoms_row.user = "Paolo De Angelis"
    if use_runtime:
        atoms_row.ctime = (
            runtime - dt.datetime(2000, 1, 1)
        ).total_seconds() / YEAR  # time since January 1. 2000
    else:
        atoms_row.ctime = ase.db.core.now()
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
    db,
    job,
    subset_name,
    task,
    add_ic=False,
    use_runtime=True,
    fulldataset_path="last_attempt/training/dataset.yaml",
    trainigset_path="last_attempt/training/dataset_1over3.yaml",
    verbose=True,
):
    if add_ic:
        add_ic_to_db(db, job, subset_name, use_runtime=use_runtime)
        if verbose:
            last_id = db.count()
            row = db.get(id=last_id)
            print(f"Added `{row.task}` of simulation: {job.path}")
            print(row_info(row))
    # Add simulation
    add_sym_to_db(
        db,
        job,
        subset_name,
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
