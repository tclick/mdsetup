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
"""Initialization subcommand for mdsetup."""
from itertools import product
from pathlib import Path

import click
from click_extra import help_option, timer_option
from loguru import logger

from .. import __copyright__, config_logger
from . import FILE_MODE


@click.command(
    "init",
    help=f"{__copyright__}\nCreate simulation subdirectories.",
    short_help="Create subdirectories for MD simulations",
)
@click.option(
    "-o",
    "--outdir",
    metavar="DIR",
    default=Path.cwd() / "amber",
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="Parent directory",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd() / Path(Path(__file__).stem[4:]).with_suffix(".log"),
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
    help="Log file",
)
@click.option(
    "-v",
    "--verbose",
    metavar="VERBOSE",
    show_default=True,
    default="INFO",
    type=click.Choice("CRITICAL ERROR WARNING INFO DEBUG".split()),
    help="Verbosity level",
)
@help_option()
@timer_option()
def cli(outdir: Path, logfile: Path, verbose: str) -> None:
    """Create simulation subdirectories.

    Parameters
    ----------
    outdir : Path
        Output directory
    logfile : Path
        Location of log file
    verbose : str
        Level of verbosity for logging output
    """
    config_logger(logfile=logfile.as_posix(), level=verbose)
    click.echo(__copyright__)

    directories = ("Prep", "Equil", "Prod", "Analysis", "Scripts")
    for _ in directories:
        directory = outdir / _
        logger.info(f"Creating {directory.as_posix()}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    # Equilibration subdirectories
    equilibration = ("min", "md")
    subsection = (1, 2, 11, 12, 13, 14, 15, 16)
    directories = (
        outdir / "Equil" / f"{x}{y:d}" for x, y in product(equilibration, subsection) if f"{x}{y:d}" != "min16"
    )
    for directory in directories:
        logger.info(f"Creating {directory.as_posix()}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    # Production subdirectories
    production = ("mdst", "mdprod")
    for _ in production:
        directory = outdir / "Prod" / _
        logger.info(f"Creating {directory.as_posix()}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    logger.success("Simulation subdirectories created.")
