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
"""Test for mdsetup.commands.create subcommand."""
import os
from pathlib import Path

import pytest
from click.testing import CliRunner
from mdsetup.commands import cmd_create

from ..datafile import TOP


class TestCreate:
    """Run test for create subcommand."""

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

        GIVEN the create subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed

        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        """
        result = cli_runner.invoke(cmd_create.cli, ["-h"])

        assert "Usage:" in result.output
        assert result.exit_code == os.EX_OK

    @pytest.mark.parametrize("sim_type", "equil prod all".split())
    def test_create(self, cli_runner: CliRunner, sim_type: str):
        """Test subcommand in an isolated filesystem.

        GIVEN a simulation type
        WHEN the create subcommand is called
        THEN write Amber simulation files in subdirectories


        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        sim_type : str
            Simulation type
        """
        with cli_runner.isolated_filesystem() as ifs:
            tmp_path = Path(ifs)
            logfile = tmp_path / "create.log"
            subdir = tmp_path / sim_type.title() if sim_type != "all" else Path(ifs) / "Prod"
            infile = {
                "prod": subdir / "mdprod" / "mdprod.in",
                "equil": subdir / "md1" / "md1.in",
                "all": subdir / "mdprod" / "mdprod.in",
            }

            result = cli_runner.invoke(
                cmd_create.cli,
                [
                    "-s",
                    TOP,
                    "-d",
                    ifs,
                    "-p",
                    "rnase2",
                    "-l",
                    logfile.as_posix(),
                    "--simprog",
                    "amber",
                    "--type",
                    sim_type,
                    "--toppar",
                    ifs,
                ],
                env={"AMBERHOME": ifs},
            )

            assert logfile.exists() and logfile.stat().st_size > 0
            assert subdir.exists() and subdir.is_dir()
            assert infile[sim_type].exists()
            assert result.exit_code == os.EX_OK

    def test_bad_simprog(self, cli_runner: CliRunner) -> None:
        """Test bad subcommand in an isolated filesystem.

        GIVEN a invalid simulation program type
        WHEN the create subcommand is called
        THEN write Amber simulation files in subdirectories

        Parameters
        ----------
        cli_runner : CliRunner
            Command-line cli_runner
        """
        with cli_runner.isolated_filesystem() as ifs:
            logfile = Path(ifs) / "simfiles.log"

            result = cli_runner.invoke(
                cmd_create.cli,
                [
                    "-s",
                    TOP,
                    "-d",
                    ifs,
                    "-p",
                    "rnase2",
                    "-l",
                    logfile.as_posix(),
                    "--simprog",
                    "badprog",
                    "--type",
                    "prod",
                    "--toppar",
                    ifs,
                ],
                env={"AMBERHOME": ifs},
            )

            assert "Error" in result.output
            assert result.exit_code != os.EX_OK
