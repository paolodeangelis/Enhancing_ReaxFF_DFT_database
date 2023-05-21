#!/usr/bin/env python

"""
Install-Jmol Script
===================

This script installs Jmol for the ASE web interface.

Usage:
------
    python install_jmol.py [-i] [-f FORMAT] [-Ns NSTART] [-Ne NEND]

Arguments:
----------
    -i, --install-pkg     Install required packages

Example:
--------
    python install_jmol.py -i
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from shutil import copyfileobj, rmtree
from typing import Optional
from zipfile import ZipFile

import requests

URL = "https://sourceforge.net/projects/jmol/files/Jmol/Version%2016.1/Jmol%2016.1.11/Jmol-16.1.11-binary.zip"
OUTFILE = "./Jmol-16.1.11-binary.zip"
OUTDIR = "./Jmol"


def install(package: str) -> list[str]:
    """
    Install a Python package using pip.

    Args:
        package (str): Package name to install.

    Returns:
        List of installed package names.

    Raises:
        CalledProcessError: If the installation fails.
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    reqs = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
    installed_packages = [r.decode().split("==")[0] for r in reqs.split()]
    return installed_packages


def message(msg: str, type: Optional[str] = None, end: str = "\n") -> None:
    """
    Display a formatted message.

    Args:
        msg (str): The message to display.
        type Optional[str]: Type of the message (info, error, warning).
        end (str): The end character to use (default: newline).
    """
    if type == "info":
        sys.stdout.write("\x1b[0;34m" + "[Info]:    " + msg + "\x1b[0m" + end)
    elif type == "error":
        sys.stderr.write("\x1b[0;31m" + "[Error]:   " + msg + "\x1b[0m" + end)
    elif type == "warning":
        sys.stderr.write("\x1b[0;33m" + "[Warning]: " + msg + "\x1b[0m" + end)
    else:
        sys.stdout.write("\x1b[4m" + msg.strip() + "\x1b[0m" + end)


parser = argparse.ArgumentParser(
    prog="Install-Jmol",
    description="Install Jmol for ASE web interface",
)

parser.add_argument("-i", "--install-pkg", help="path to the configurations", default=False, action="store_true")

message(" START ".center(120, "="))

args = parser.parse_args()
install_pkg = args.install_pkg

try:
    import ase.db
except ImportError:
    if not install_pkg:
        message("`ase` package is not installed", type="error")
        message(
            "1) Please make sure that you are using the correct Python interpreter or virtual environment.",
            type="error",
        )
        message(
            "2) If you are sure that you are using the correct Python interpreter or virtual environment,", type="error"
        )
        message(
            "   please install it using `pip install ase`, or use the -i or --install-pkg option when running",
            type="error",
        )
        message(
            "   this script",
            type="error",
        )
        exit()
    else:
        message("`ase` package is not installed, installing it now", type="warning")
        install("ase==3.22.1")
        import ase.db

        message("`ase` package installed and imported", type="info")

try:
    from tqdm import tqdm
    from tqdm.utils import CallbackIOWrapper
except ImportError:
    if not install_pkg:
        message("`tqdm` package is not installed", type="error")
        message(
            "Please install it using `pip install tqdm`, or use the -i or --install-pkg option when running",
            type="error",
        )
        message(
            "   this script",
            type="error",
        )
        exit()
    else:
        message("`tqdm` package is not installed, installing it now", type="warning")
        install("tqdm")
        from tqdm import tqdm
        from tqdm.utils import CallbackIOWrapper

        message("`tqdm` package installed and imported", type="info")


def download(url: str, fname: str, msg: str) -> None:
    """
    Download a file from a given URL.

    Args:
        url (str): URL of the file to download.
        fname (str): File name to save the downloaded file.
        msg (str): Message to display during the download.
    """
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=msg,
        total=total,
        bar_format="{desc:<18} {percentage:3.0f}%|{bar:40}{r_bar}",
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def extractall(fzip: str, dest: str, msg: str = "Extracting") -> None:
    """
    Extract a zip file to a given destination.

    Args:
        fzip (str): Path to the zip file.
        dest (str): Destination directory to extract the files.
        msg (str): Message to display during the extraction (default: 'Extracting').
    """
    dest_ = Path(dest).expanduser()
    with ZipFile(fzip) as zipf, tqdm(
        desc=msg,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        bar_format="{desc:<18} {percentage:3.0f}%|{bar:40}{r_bar}",
        total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
    ) as pbar:
        for i in zipf.infolist():
            if not getattr(i, "file_size", 0):  # directory
                zipf.extract(i, os.fspath(dest_))
            else:
                with zipf.open(i) as fi, open(os.fspath(dest_ / Path(i.filename)), "wb") as fo:
                    copyfileobj(CallbackIOWrapper(pbar.update, fi), fo)


if os.path.isfile(OUTFILE):
    message(f"File {OUTFILE} already exists, skipping download", type="warning")
    message("Do you want to re-download the file? (y/n): ", type="warning", end="")
    answer = input()
    if answer.lower() == "y":
        os.remove(OUTFILE)
        message(f"File {OUTFILE} removed", type="warning")

if not os.path.isfile(OUTFILE):
    message(f"Downloading Jmol binary file from SourceForge ({OUTFILE})", type="info")
    download(URL, OUTFILE, "Downloading Jmol")

message("Extracting Jmol binary file", type="info")
if os.path.isdir(OUTDIR):
    message(f"Folder {OUTDIR} already exists, it will be removed before extraction", type="warning")
    rmtree(OUTDIR)
    message(f"Folder {OUTDIR} deleted", type="warning")

extractall(OUTFILE, "Jmol", msg="Extracting")
jsmol_zip_path = os.path.join("Jmol", "jmol-16.1.11", "jsmol.zip")
jsmol_unzip_path = os.path.join("Jmol", "jmol-16.1.11", ".")
message("Extracting Jsmol binary file", type="info")
extractall(jsmol_zip_path, jsmol_unzip_path, msg="Extracting")
message("Installing jsmol into ASE database", type="info")

src = os.path.abspath(os.path.join(jsmol_unzip_path, "jsmol"))
dst = os.path.join(os.path.dirname(ase.db.__file__), "static", "jsmol")
if os.path.islink(dst):
    message("Symbolic link already exists, it will be removed", type="warning")
    os.remove(dst)
    message(f"Symbolic link {dst} removed", type="warning")
os.symlink(src, dst)
message("Symbolic link created:", type="info")
message(f"{src} -> {dst}", type="info")
message(" DONE ".center(120, "="))
