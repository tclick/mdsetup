# Molecular Dynamics Setup

[![PyPI](https://img.shields.io/pypi/v/mdsetup.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/mdsetup.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/mdsetup)][pypi status]
[![License](https://img.shields.io/pypi/l/mdsetup)][license]

[![Read the documentation at https://mdsetup.readthedocs.io/](https://img.shields.io/readthedocs/mdsetup/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/tclick/mdsetup/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/tclick/mdsetup/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/mdsetup/
[read the docs]: https://mdsetup.readthedocs.io/
[tests]: https://github.com/tclick/mdsetup/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/tclick/mdsetup
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Introduction

Prepares a system for molecular dynamics (MD). `mdsetup` can initialize a directory
structure for storing the MD data, solvate a system, and write various input files that
can be used with different simulations packages: Amber, CHARMM, or Gromacs. The
simulation protocol was originally developed in the lab of Dr.
[Pratul Agarwal](https://hpcc.okstate.edu/pratul_agarwal.html) at
Oklahoma State University.

## Features

- Initialize of molecular dynamics (MD) subdirectories for simulations
- Create various script files to use with Amber, CHARMM, or Gromacs
- Solvate and neutralize a system

## Requirements

- Python 3.10+
- click-extra
- MDAnalysis 2.5+
- jinja2

## Installation

You can install _Molecular Dynamics Setup_ via [pip] from [PyPI]:

```console
$ pip install mdsetup
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [GPL 3.0 license][license],
_Molecular Dynamics Setup_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/tclick/mdsetup/issues
[pip]: https://pip.pypa.io/

---

## Understanding the Equilibration Protocol[[1](#1)]

### Summary

- Remove bad contacts or steric clashes in models or X-ray cyrstal structures
- Allow added hydrogens to adopt reasonable conformations
- For explicit simulations allow the solvent to occupy reasonable volume

Remove steric clashes: The starting point for MD simulations is a structure obtained
from X-ray crystallography (or Nuclear Magnetic Resonance, NMR). This technique is used
to assign the position of atoms (nucleii) based on fitting to electron density. The
fitting can involve errors due to inherent errors related to data collection (or other
real effects such as protein motions). There errors could show up as close contacts
between atoms or steric clashes between neighbors. If one were to start with such close
contacts, there would large forces involved causing unrealistic movements. Therefore,
before any type of research quality MD simulations (called production runs) can be
performed, the prepared systems needs to be equilibrated to remove any close contacts.

In other modeling cases, ligands or different members of protein complex are obtained
from different PDB files, therefore, the starting model could also results in steric
clashes. The procedure to remove these clashes would be part of the equilibration
protocol as well.

Relax added Hydrogen atoms: One limitation of the X-ray crystallography is that it does
not allow obtaining information about the position of hydrogens in the system.
Therefore, based on the position of heavy atoms in the solved crystal structure,
software is used to add hydrogen atoms. The added hydrogen could start from unoptimal
positions. Therefore to similar to removing close contacts, equilibration also allows
hydrogens to adopt optimal conformations.

Relax added solvent molecules and counter-ions: In addition if the system has explicit
water and ions, they are generally added at random positions. One of the most common way
of immersing protein complex into a pre-defined water box is by cutting out van der
Waals radius envelope of protein complex and immersing it in the water box. (Imagine
this you are carving out an empty space with laser in a block of ice.) Doing this would
leave some empty space and cause pockets of empty space (bubbles) to form and have lower
density than expected. This also needs to be gently removed during the equilibration
process.

The protocols for equilibration vary by the labs. We have found that starting from X-ray
structure and holding the protein fixed with restraints and releasing them slowly helps
in removing bad contacts as well as allow water to equilibrate around the protein.

For equilibration, first only the water molecules were minimized by using the steepest
descent method for the first 500 steps, followed by the conjugate gradient method until
the root mean square (RMS) of the Cartesian elements of the gradient was >0.25
kcal/mol-Å. Solute atoms alone were then minimized in the same way to release any close
contacts in the crystal structures. A 25 ps MD step with a temperature ramp was then
used to gradually raise the temperature of the whole system to 300 K, followed by a 25
ps constant pressure MD step,41 in which the water molecules were allowed to move
unrestrained in order to fill in any vacuum pockets. Five additional steps of
equilibration at constant volume were performed, each step consisting of an energy
minimization (threshold of 0.001 kcal/moll-Å) followed by a 5 ps MD. Harmonic positional
restraints were applied on solute atoms during these equilibration steps. The initial
force constant was 100 kcal/moll-Å<sup>2</sup> and it was scaled by 0.5 after each
equilibration step. After four steps of this type (with force constants of 100, 50, 25,
and 12.5 kcal/mol-Å<sup>2</sup>), the final equilibration step was performed without
any positional restraints. Another MD step with a temperature ramp over 25 ps was used
to readjust the temperature to 300 K, followed by a 25 ps constant pressure MD step to
fill any remaining vacuum pockets

<a id="1">[1]</a>
The text was taken from the Agarwal lab wiki.

<!-- github-only -->

[license]: https://github.com/tclick/mdsetup/blob/main/LICENSE.md
[contributor guide]: https://github.com/tclick/mdsetup/blob/main/CONTRIBUTING.md
[command-line reference]: https://mdsetup.readthedocs.io/en/latest/usage.html
