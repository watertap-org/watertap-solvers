#################################################################################
# WaterTAP Copyright (c) 2020-2023, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory, Oak Ridge National Laboratory,
# National Renewable Energy Laboratory, and National Energy Technology
# Laboratory (subject to receipt of any required approvals from the U.S. Dept.
# of Energy). All rights reserved.
#
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license
# information, respectively. These files are also available online at the URL
# "https://github.com/watertap-org/watertap/"
#################################################################################

from dataclasses import dataclass
from functools import cached_property
import os
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest

# this needs to be done explicitly here since watertap.core.util.model_debug_mode is only imported in a subprocess
pytest.importorskip(
    "IPython", reason="The model debug mode functionality depends on IPython"
)


_INDENT: str = " " * 4


@dataclass
class IPythonComms:
    statements: List[str]
    error_file_path: Path
    message_when_no_errors: str = "NO ERRORS WHATSOEVER"

    def __post_init__(self):
        self.error_file_path.touch()

    @cached_property
    def lines(self) -> List[str]:
        return [
            f"to_print = r'''{self.message_when_no_errors}'''",
            "try:",
            *[f"{_INDENT}{smt}" for smt in self.statements],
            "except Exception as e:",
            f"{_INDENT}to_print = str(e)",
            f"print(to_print, file=open(r'{self.error_file_path}', 'w'))",
            "exit",
        ]

    @cached_property
    def for_display(self) -> str:
        return "\n".join(self.lines)

    @cached_property
    def for_stdin(self) -> str:
        # to work properly in IPython, there needs to be trailing newline as well
        return "\n".join(f"{line}\n" for line in self.lines)

    @cached_property
    def error_text(self) -> str:
        return self.error_file_path.read_text().strip()


@pytest.mark.parametrize(
    "path_to_script",
    [
        "model_debug_example_script.py",
    ],
    ids=os.fspath,
)
def test_debug_mode(path_to_script: Path, tmp_path: Path):
    path_to_script = Path(path_to_script)
    if not path_to_script.is_absolute():
        path_to_script = Path(__file__).parent / path_to_script
    script = path_to_script.read_text()

    ipy = IPythonComms(
        statements=[
            "import idaes",
            "assert isinstance(dt, idaes.core.util.model_diagnostics.DiagnosticsToolbox)",
            "assert isinstance(blk, pyo.Block)",
            "assert isinstance(blk.model(), pyo.ConcreteModel)",
        ],
        error_file_path=tmp_path / "errors.txt",
    )

    proc = subprocess.Popen(
        [
            sys.executable,
            "-c",
            script,
        ],
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate(input=ipy.for_stdin, timeout=30)
    if out:
        print(out)
    if err:
        print(err)
    assert ipy.error_text == ipy.message_when_no_errors
