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
"""Test for mdsetup.commands.cmd_solvate subcommand."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from mdsetup.commands import cmd_solvate

from ..datafile import PDB, TOP


class TestSolvate:
    """Run test for solvate subcommand."""

    @pytest.fixture()
    def cli_runner(self) -> CliRunner:
        """Fixture for testing `click` commands.

        Returns
        -------
        CliRunner
            CLI runner
        """
        return CliRunner()

    def test_help(self, cli_runner: CliRunner):
        """Test help output.

        GIVEN the solvate subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed

        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        """
        result = cli_runner.invoke(cmd_solvate.cli, ["-h"])

        assert "Usage:" in result.output
        assert result.exit_code == os.EX_OK

    def test_solvate(self, cli_runner: CliRunner, mocker):
        """Test subcommand in an isolated filesystem.

        GIVEN a topology and structure file
        WHEN the solvate subcommand is called
        THEN the system is neutralized and solvated.

        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        """
        which = mocker.patch.object(shutil, "which", autospec=True)
        run = mocker.patch.object(subprocess, "run", autospec=True)

        with cli_runner.isolated_filesystem() as ifs:
            tmp_path = Path(ifs)
            prefix = Path("solvate")
            logfile = tmp_path / prefix.with_suffix(".log")
            infile = tmp_path / prefix.with_suffix(".in")

            result = cli_runner.invoke(
                cmd_solvate.cli,
                [
                    "-s",
                    TOP,
                    "-f",
                    PDB,
                    "-o",
                    ifs,
                    "-p",
                    prefix.as_posix(),
                    "-l",
                    logfile.as_posix(),
                    "--simprog",
                    "amber",
                    "--toppar",
                    ifs,
                ],
                env={"AMBERHOME": ifs},
            )

            assert logfile.exists() and logfile.stat().st_size > 0
            assert infile.exists() and infile.stat().st_size > 0
            assert not (tmp_path / "tleap").exists()
            assert result.exit_code == os.EX_OK

        which.assert_called()
        run.assert_called()

    def test_no_amber(self, cli_runner: CliRunner, mocker):
        """Test subcommand in an isolated filesystem.

        GIVEN a topology and structure file
        WHEN the solvate subcommand is called
        THEN the system is neutralized and solvated.

        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        """
        with cli_runner.isolated_filesystem() as ifs:
            tmp_path = Path(ifs)
            prefix = Path("solvate")
            logfile = tmp_path / prefix.with_suffix(".log")
            tmp_path / prefix.with_suffix(".in")

            with pytest.raises(FileNotFoundError):
                cli_runner.invoke(
                    cmd_solvate.cli,
                    [
                        "-s",
                        TOP,
                        "-f",
                        PDB,
                        "-o",
                        ifs,
                        "-p",
                        prefix.as_posix(),
                        "-l",
                        logfile.as_posix(),
                        "--simprog",
                        "amber",
                        "--toppar",
                        ifs,
                    ],
                    env={"AMBERHOME": ifs},
                )
