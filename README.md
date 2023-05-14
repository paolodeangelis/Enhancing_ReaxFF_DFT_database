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

This repository contains the database used for retraining the ReaxFF force field for the inorganic compound LiF. The database is intended to enhance the accuracy and reliability of ReaxFF calculations for LiF.

## Installation

To use the database and interact with it, you need to have the following Python requirements installed:

- Python 3.6 or above
- ASE (Atomic Simulation Environment) library
- ReaxFF library

You can install the required Python packages using pip:

```shell
pip install ase
pip install reaxff
```

## Folder Structure

The repository has the following folder structure:

```
├── database.db
├── README.md
├── reaxff_files
│   ├── parameters.prm
│   └── reactive_force_field.geo
└── web_interface
    ├── index.html
    └── scripts.js
```

- `database.db`: This is the SQLite database file containing the retraining data for the ReaxFF force field.
- `reaxff_files`: This folder contains the ReaxFF parameter and force field files required for the force field calculations.
  - `parameters.prm`: The ReaxFF parameter file.
  - `reactive_force_field.geo`: The ReaxFF force field file.
- `web_interface`: This folder contains the web interface files for interacting with the database.
  - `index.html`: The HTML file for the web interface.
  - `scripts.js`: The JavaScript file for the web interface.

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
db = connect('database.db')

# Query the database
results = db.select('formula = "LiF"')

# Iterate over the results
for row in results:
    print(f'ID: {row.id}, Energy: {row.energy}')
```

Modify the code according to your specific needs to perform desired operations on the database.

## Contributing

If you would like to contribute to the Enhancing ReaxFF DFT Database, feel free to submit pull requests or open issues in the repository.

## License

The contents of this repository are licensed under the [Creative Commons Attribution 4.0 International License][cc-by].

<hr width="100%">
<p style="text-align:left;">
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0; height:35px" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>
<span style="float:right;">
    &nbsp;
    <a target="_blank" href="https://www.big-map.eu/">
        <img style="height:35px" src="assets/img//logo-bigmap.png" alt="BIG MAP site" >
    </a>
    &nbsp;
    <a target="_blank" href="https://areeweb.polito.it/ricerca/small/">
        <img style="height:35px" src="assets/img//logo-small.png" alt="SMALL site" >
    </a>
    &nbsp;
    <a target="_blank" href="https://www.polito.it/">
        <img style="height:35px" src="assets/img//logo-polito.png" alt="POLITO site" >
    </a>
    </span>
</p>

<!-- [![CC BY 4.0][cc-by-image]][cc-by] -->

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg