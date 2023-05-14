# Enhancing ReaxFF DFT database
<p style="text-align:left;">
    <a target="_blank" href="https://python.org"><img
        src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&amp;logoColor=white"
        alt="Made with Python" />
    </a>
    <a target="_blank" href="https://www.linux.org/"><img
        src="https://img.shields.io/badge/OS-Linux-orange?logo=linux&amp;logoColor=white"
        alt="OS - Linux" />
    </a>
    <a target="_blank" href="/CONTRIBUTING.md"><img
        src="https://img.shields.io/badge/contributions-open-green"
        alt="Contributions - welcome" />
    </a>
    <a target="_blank" href="https://github.com/psf/black"><img
        src="https://img.shields.io/badge/code%20style-black-000000.svg"
        alt="Code style - black" />
    </a>
    <a target="_blank" href="https://results.pre-commit.ci/badge/github/paolodeangelis/Enhancing_ReaxFF_DFT_database/main.svg"><img
        src="https://results.pre-commit.ci/badge/github/paolodeangelis/Enhancing_ReaxFF_DFT_database/main.svg"
        alt="pre-commit.ci status" />
    </a>
    <a target="_blank" href="http://creativecommons.org/licenses/by/4.0/"><img
        src="https://img.shields.io/badge/license-CC%20BY%204.0-lightgray"
        alt="License - CC BY 4.0" />
    </a>
</p>

This repository contains the database used for retraining the ReaxFF force field for the inorganic compound LiF.
The database is intended to enhance the accuracy and reliability of ReaxFF calculations for LiF, which results and method was published on the article [Enhancing ReaxFF for Lithium-ion battery simulations: An interactive reparameterization protocol][article-doi].

This database was make using the simulation obtained using the protocol published in [Enhancing ReaxFF repository][enhancing-reaxFF-repository].

## Installation

To use the database and interact with it, ensure that you have the following Python requirements installed:

**Minimum Requirements:**
- Python 3.9 or above
- Atomic Simulation Environment (ASE) library
- Jupyter Lab

**Requirements for Rerunning or Performing New Simulations:**
- SCM (Software for Chemistry & Materials) Amsterdam Modeling Suite
- PLAMS (Python Library for Automating Molecular Simulation) library

You can install the required Python packages using pip:

```shell
pip install -r requirements.txt
```
> **Warning**
>
> Make sure to have the appropriate licenses and installations of SCM Amsterdam Modeling Suite and any other necessary software for running simulations.

## Folder Structure

The repository has the following folder structure:

```
.
├── LICENSE
├── README.md
├── requirements.txt
├── assets
├── data
│   └── LiF.db
├── notebooks
└── tools
    └── plasm_experimental
```

- `LICENSE`: This file contains the license information for the repository (CC BY 4.0). It specifies the terms and conditions under which the contents of the repository are distributed and used.
- `README.md`: This file.
- `requirements.txt`: This file lists the required Python packages and their versions. (see [installation section](#installation))
- `assets`: This folder contains any additional assets, such as images or documentation, related to the repository.
- `data`:
  - `LiF.db`: file is an SQLite database file. It contains the retraining data for the ReaxFF force field specifically for the inorganic compound LiF.
- `notebooks`: This folder is dedicated to Jupyter notebooks that demonstrate the usage and analysis of the database. It can be used as a starting point for exploring and manipulating the data.
- `tools`:
  - `plasm_experimental`: This subfolder houses experimental tools or scripts that can be used for experimental data analysis or simulations. It may contain scripts specific to the LiF database or ReaxFF simulations.


## Interacting with the Database

There are three ways to interact with the database: using the ASE db terminal command, the web interface, and the ASE Python interface.

### ASE db Terminal Command

To interact with the database using the ASE db terminal command, follow these steps:

1. Open a terminal and navigate to the directory containing the `database.db` file.
2. Run the following command to start the ASE db terminal:

   ```shell
   ase db database.db
   ```

3. You can now use the available commands in the terminal to query and manipulate the database.

### Web Interface

To interact with the database using the web interface, follow these steps:

1. Open the `index.html` file located in the `web_interface` folder using a web browser.
2. Use the provided forms and buttons in the web interface to query and modify the database.

### ASE Python Interface

To interact with the database using the ASE Python interface, you can use the following example code:

```python
from ase.db import connect

# Connect to the database
db = connect("database.db")

# Query the database
results = db.select('formula = "LiF"')

# Iterate over the results
for row in results:
    print(f"ID: {row.id}, Energy: {row.energy}")
```

Modify the code according to your specific needs to perform desired operations on the database.

## Contributing

If you would like to contribute to the Enhancing ReaxFF DFT Database, feel free to submit pull requests or open issues in the repository.

## License

The contents of this repository are licensed under the [Creative Commons Attribution 4.0 International License][cc-by].

## Acknowledgements

This project has received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189).
The project is part of [BATTERY 2030+](https://battery2030.eu/), the large-scale European research initiative for inventing the sustainable batteries of the future.

The authors also acknowledge that the simulation results of this database have been achieved using the [DECI](https://prace-ri.eu/hpc-access/deci-access/) resource [ARCHER2](https://www.archer2.ac.uk/) based in UK at [EPCC](https://www.epcc.ed.ac.uk/) with support from the [PRACE](https://prace-ri.eu/) aisbl.

<hr width="100%">
<div style="display: flex; justify-content: space-between; align-items: center;">
    <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0; height:35px" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>
   <span style="float:right;">
    &nbsp;
    <a rel="big-map" href="https://www.big-map.eu/">
        <img style="border-width:0; height:35px" src="assets/img//logo-bigmap.png" alt="BIG MAP site" >
    </a>
    &nbsp;
    <a rel="small" href="https://areeweb.polito.it/ricerca/small/">
        <img style="border-width:0; height:35px" src="assets/img//logo-small.png" alt="SMALL site" >
    </a>
    &nbsp;
    <a rel="polito"href="https://www.polito.it/">
        <img style="border-width:0; height:35px" src="assets/img//logo-polito.png" alt="POLITO site" >
    </a>
</span>
</div>

<!-- [![CC BY 4.0][cc-by-image]][cc-by] -->

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
[article-doi]: https://doi.org/TBD
[enhancing-reaxFF-repository]: https://github.com/paolodeangelis/Enhancing_ReaxFF
