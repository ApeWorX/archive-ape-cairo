import os
from pathlib import Path

import ape
import pytest
from ape.utils import get_all_files_in_directory

PROJECT_DIRECTORY = Path(__file__).parent
SOURCE_CODE_DIRECTORY = PROJECT_DIRECTORY / "contracts"

SOURCE_FILES = [
    Path(str(p).replace(str(SOURCE_CODE_DIRECTORY), "").strip("/"))
    for p in get_all_files_in_directory(SOURCE_CODE_DIRECTORY)
]


# NOTE: Params converted to strings to looks nicer in pytest case outputs
@pytest.fixture(params=[str(p) for p in SOURCE_FILES])
def contract(request):
    yield (SOURCE_CODE_DIRECTORY / request.param).absolute()


@pytest.fixture(scope="session", autouse=True)
def in_tests_directory():
    """
    Ensures tests are run from 'ape-cairo/tests/' directory.
    """
    start_path = Path.cwd()
    os.chdir(PROJECT_DIRECTORY)

    with ape.config.using_project(PROJECT_DIRECTORY):
        yield

    os.chdir(start_path)


@pytest.fixture(autouse=True)
def clean_cache():
    """
    Use this fixture to ensure a project
    does not have a cached compilation.
    """
    cache_file = PROJECT_DIRECTORY / ".build" / "__local__.json"
    if cache_file.exists():
        cache_file.unlink()

    yield

    if cache_file.exists():
        cache_file.unlink()


@pytest.fixture
def project():
    return ape.project


@pytest.fixture
def compiler():
    return ape.compilers.registered_compilers[".cairo"]
