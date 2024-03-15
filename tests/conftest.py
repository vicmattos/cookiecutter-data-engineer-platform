from contextlib import contextmanager
from pathlib import Path
import os
import subprocess
import shlex

import pytest
from cookiecutter.utils import rmtree


@pytest.fixture
def bake_in_temp_dir():
    @contextmanager
    def bake_in_temp_dir(cookies, *args, **kwargs):
        """
        Delete the temporal directory that is created when executing the tests
        """
        result = cookies.bake(*args, **kwargs)
        try:
            yield result
        finally:
            rmtree(str(result.project_path))

    return bake_in_temp_dir


@pytest.fixture
def run_inside_dir():
    def run_inside_dir(command: str, dirpath: Path) -> int:
        """
        Run a command from inside a given directory, returning the exit status
        """
        old_path = os.getcwd()
        try:
            os.chdir(dirpath)
            ret = subprocess.check_call(shlex.split(command))
        finally:
            os.chdir(old_path)
        return ret

    return run_inside_dir


@pytest.fixture
def text_in_file():
    def text_in_file(txt: str, file: Path, not_in: bool = False) -> bool:
        """
        Check if text is inside file
        """
        with open(file) as f:
            ret = any(txt in line for line in f)
            return not ret if not_in else ret

    return text_in_file
