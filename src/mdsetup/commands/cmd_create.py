# ------------------------------------------------------------------------------
#  mdsetup
#  Copyright (c) 2023 Timothy H. Click, Ph.D.
#
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of the author nor the names of its contributors may be used
#  to endorse or promote products derived from this software without specific
#  prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.
# ------------------------------------------------------------------------------
"""Create input files for simulations.

The `create` subcommand writes several input files for usage with different simulation packages. The user can output
files that will either be used with Amber, CHARMM or Gromacs; the protocol follows procedures laid forth by the lab of
Dr. Pratul Agarwal at Oklahoma State University.
"""
import os
import time
from pathlib import Path

import click
import MDAnalysis as mda
from click_extra import help_option, timer_option
from loguru import logger

from .. import __copyright__, config_logger
from ..libs.template import write_template
from . import FILE_MODE


@click.command(
    "create",
    help="Prepare various Amber input files to run simulations",
    short_help="Prepare input files for simulation.",
)
@click.option(
    "-s",
    "--topology",
    metavar="FILE",
    default="amber.parm7",
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="Topology file",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    default=Path.cwd().joinpath(Path(Path(__file__).stem[4:]).with_suffix(".log")),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, writable=True, resolve_path=True, path_type=Path),
    help="Log file",
)
@click.option(
    "-d",
    "--outdir",
    metavar="DIR",
    default=Path.cwd(),
    show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    help="Simulation subdirectory",
)
@click.option(
    "-p",
    "--prefix",
    metavar="PREFIX",
    default=Path.cwd().stem,
    show_default=True,
    help="Prefix for various output files",
)
@click.option(
    "--temp1",
    metavar="TEMP",
    default=100.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Initial temperature (K)",
)
@click.option(
    "--temp2",
    metavar="TEMP",
    default=300.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Final temperature (K)",
)
@click.option(
    "--force",
    metavar="FORCE",
    default=100.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Restraint force (kcal/mol/A^2",
)
@click.option(
    "--type",
    "outtype",
    default="all",
    show_default=True,
    type=click.Choice("equil prod scripts all".split(), case_sensitive=False),
    help="Which output files to create",
)
@click.option(
    "--simprog",
    "sim_prog",
    metavar="PROG",
    default="amber",
    type=click.Choice("amber charmm gmx".split(), case_sensitive=False),
    help="Simulation program",
)
@click.option(
    "--toppar",
    metavar="DIR",
    default=Path(Path.home().root) / "opt" / "local" / "charmm" / "toppar",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    help="Topology/parameter directory",
)
@click.option("--ff", metavar="FF", default=36, type=click.IntRange(min=22, clamp=True), help="CHARMM force field")
@click.option(
    "-v",
    "--verbose",
    metavar="VERBOSE",
    show_default=True,
    default="INFO",
    type=click.Choice("CRITICAL ERROR WARNING INFO DEBUG".split()),
    help="Verbosity level",
)
@help_option
@timer_option
def cli(
    topology: Path,
    outdir: Path,
    prefix: str,
    temp1: float,
    temp2: float,
    force: float,
    logfile: Path,
    outtype: str,
    sim_prog: str,
    toppar: Path,
    ff: int,
    verbose: str,
) -> None:
    """Prepare various Amber input files to run simulations.

    Using various options, multiple input files are created for use with either Amber, CHARMM, or Gromacs. The files
    will be saved in subdirectories, which allows for separation of output files.

    Parameters
    ----------
    topology : Path
        topology filename
    outdir : Path
        Output directory
    prefix : str
        Prefix for script files
    temp1 : float, default=100.0
        Initial temperature (in K)
    temp2 : float, default=300.0
        Final temperature (in K)
    force : float, default=1.0
        Force restraint
    logfile : Path
        Log file
    outtype : str, default='all'
        Scripts to process
    sim_prog : str, default='amber'
        Simulation program for output files
    toppar : Path
        Directory for CHARMM force field files
    ff : int, default=36
        Force field number for CHARMM force field files
    verbose : str
        Level of verbosity for logging output
    """
    config_logger(logfile=logfile.as_posix(), level=verbose)
    click.echo(__copyright__)

    universe = mda.Universe(topology)
    solute = universe.select_atoms("not resname Na+ Cl- WAT")
    ions = universe.select_atoms("resname Na+ Cl-")
    solvent = universe.select_atoms("resname WAT")

    data = {
        "temp1": temp1,
        "temp2": temp2,
        "res0": solute[0],
        "res1": solute[-1],
        "ions0": ions[0],
        "ions1": ions[-1],
        "solvent0": solvent[0],
        "solvent1": solvent[-1],
        "force": force,
        "simdir": outdir,
        "prefix": prefix,
        "toppar": toppar,
        "charmm_ff": ff,
        "year": time.strftime("%Y"),
    }

    if sim_prog == "amber":
        try:
            data["amberhome"] = Path(os.environ["AMBERHOME"])
            logger.debug(f"""AMBERHOME = {os.environ["AMBERHOME"]}""")
        except KeyError:
            logger.opt(exception=True).exception("AMBERHOME environment variable not defined.")
            raise

    template_name = {
        "equil": ("equil",),
        "prod": ("prod",),
        "scripts": ("scripts",),
        "all": ("equil", "prod", "scripts"),
    }

    for _ in template_name.get(outtype.lower(), "all"):
        template_dir = Path("templates") / sim_prog / _
        subdir = outdir / _.title()
        subdir.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

        logger.info(f"Template directory: {template_dir.as_posix()}")
        logger.info(f"Output files: {subdir.as_posix()}")
        write_template(data, subdir=subdir, package_path=template_dir, template=_)

    # # Write the shell scripts
    if outtype == "scripts" or outtype == "all":
        logger.debug(f"Changing file permissions to {FILE_MODE}")
        subdir = outdir / "Scripts"
        for _ in subdir.glob("*.sh"):
            _.chmod(mode=FILE_MODE)
