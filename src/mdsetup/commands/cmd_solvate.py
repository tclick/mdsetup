# ------------------------------------------------------------------------------
#  $ProjectName$
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
"""Neutralize and solvate a system.

The `solvate` subcommand neutralizes and solvates a system. The system can be prepared for Amber, CHARMM , or Gromacs.
"""
import shutil
from pathlib import Path

import click
from click_extra import help_option, timer_option
from loguru import logger

from .. import __copyright__, config_logger
from ..libs.template import write_template
from ..libs.utils import run_command


@click.command(
    "solvate",
    help="Neutraolize and solvate a system.",
    short_help="Neutraolize and solvate a system.",
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
    "-f",
    "--infile",
    metavar="FILE",
    default=Path.cwd() / "input.pdb",
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="Input file",
)
@click.option(
    "-o",
    "--outdir",
    metavar="DIR",
    default=Path.cwd(),
    show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    help="Output subdirectory",
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
    "-p",
    "--prefix",
    metavar="PREFIX",
    default="solvate",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Prefix for output files",
)
@click.option(
    "--simprog",
    "sim_prog",
    metavar="PROG",
    default="amber",
    type=click.Choice("amber charmm gromacs".split(), case_sensitive=False),
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
    infile: Path,
    outdir: Path,
    logfile: Path,
    prefix: Path,
    sim_prog: str,
    toppar: Path,
    ff: int,
    verbose: str,
) -> None:
    """Neutralize and solvate a system.

    Parameters
    ----------
    topology : Path
        topology filename
    infile : Path
        structure filename
    outdir : Path
        Output directory
    logfile : Path
        Log file
    prefix : Path
        Prefix for script files
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

    filename = outdir / prefix.with_suffix(".in")
    logname = outdir / prefix.with_suffix(".log")
    data = {"input": infile, "prefix": prefix.as_posix(), "toppar": toppar, "ff": ff}

    templates = Path("templates")
    template_subdir = Path(sim_prog) / "leap" if sim_prog == "amber" else Path(sim_prog) / "solvate"
    package_path = templates / template_subdir

    logger.info(f"Writing solvation script to {filename}")
    write_template(data, subdir=outdir, package_path=package_path, template="solvate")

    # Moves file to specified location and removes unnecessary subdirectory.
    shutil.move(outdir / "solvate" / "solvate.in", filename)
    extra_dirs = ("fixed", "solvate", "tleap")
    for _ in extra_dirs:
        shutil.rmtree(outdir / _, ignore_errors=True)

    logger.info("Adding ions and solvating the system")
    command = {"amber": "tleap"}
    run_command(command[sim_prog], infile=filename, cmdlog=logname)
