#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path

import asserts
import pkg_resources
import pytest
from test_repo import repo  # noqa: F401


test_script = pkg_resources.resource_filename(
    "buck_e2e.repo_end_to_end_test", "test_script.py"
)
os.environ["TEST_BUCK_BINARY"] = test_script


@pytest.mark.asyncio
async def test_repo_build(repo):
    _create_file(Path(repo.cwd), Path("target_file_success"), 0)
    result = await (await repo.build("//:target_file_success")).wait()
    assert "target_file_success" in result.get_stdout(), result.get_stderr()
    asserts.assert_build_success(result)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=AssertionError)
async def test_repo_build_failure(repo):
    _create_file(Path(repo.cwd), Path("target_file_failure"), 1)
    result = await (await repo.build("//:target_file_failure")).wait()
    assert "target_file_failure" in result.get_stdout()
    asserts.assert_build_success(result)


def _create_file(dirpath: Path, filepath: Path, exitcode: int) -> None:
    """ Writes out a message to a file given the path"""
    with open(dirpath / filepath, "w") as f1:
        target_name = str(filepath)
        status = "FAIL" if "failure" in target_name else "PASS"
        result_type = (
            "FAILURE"
            if "fail" in target_name
            else ("SUCCESS" if "success" in target_name else "EXCLUDED")
        )
        message = f"{target_name}\n{status}\n{result_type}\n{exitcode}"
        f1.write(message)