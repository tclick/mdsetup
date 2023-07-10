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
"""Run Amber command `tleap`."""
import shutil
import subprocess
from pathlib import Path

from loguru import logger


def run_command(command: str, infile: Path, cmdlog: Path) -> None:
    """Run shell command.

    Parameters
    ----------
    command : str
        shell command
    infile : Path
        input file
    cmdlog : Path
        output from subprocess

    Raises
    ------
    FileNotFoundError
        if command is not found
    """
    try:
        logger.info("Generating AMBER topology and coordinate files.")
        cmd = shutil.which(command)
        if cmd is None:
            raise FileNotFoundError  # noqa: TRY301

        with cmdlog.open("a") as log:
            logger.info(f"Running {cmd}")
            subprocess.run(
                (cmd, "-f", infile.as_posix()),  # noqa: S603
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
    except FileNotFoundError:
        logger.opt(exception=True).exception(f"Could not find {command}")
        raise
    except subprocess.CalledProcessError:
        logger.opt(exception=True).exception(f"Could not run {command}")
        raise
