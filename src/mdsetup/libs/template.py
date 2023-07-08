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
"""Create input files from Jinja2 template files."""
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, Template, TemplateNotFound
from loguru import logger

from ..commands import FILE_MODE


def write_template(data: dict[str, Any], subdir: Path, package_path: Path, template: str) -> None:
    """Write an Amber file from a template.

    Parameters
    ----------
    data : Dict[str, Any]
        information for the template file
    subdir : Path
        Output directory
    package_path : Path
        Location of template file
    template : str
        Template filename stem

    Raises
    ------
    TemplateNotFound
        if template is not found
    """
    try:
        loader = PackageLoader("mdsetup", package_path=package_path.as_posix())
        env = Environment(loader=loader, autoescape=True)
        for _ in loader.list_templates():
            filename = Path(_)
            subdirectory = subdir / filename.stem if "Scripts" not in (subdir / filename.stem).as_posix() else subdir
            subdirectory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)
            input_file = (
                subdirectory / filename.with_suffix(".sh")
                if "scripts" in package_path.as_posix()
                else subdirectory / filename.with_suffix(".in")
            )

            with input_file.open(mode="w", encoding="utf-8") as infile:
                template_output: Template = env.get_template(filename.as_posix())
                logger.info(f"Writing script to {input_file}")
                print(template_output.render(data=data), file=infile)
    except TemplateNotFound:
        logger.exception(f"Could not load {template}.jinja2", exc_info=True)
        raise
