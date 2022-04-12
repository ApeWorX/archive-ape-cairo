import os
from pathlib import Path

import ape
import pytest

PROJECT_DIRECTORY = Path(__file__).parent
SOURCE_CODE_DIRECTORY = PROJECT_DIRECTORY / "contracts"


@pytest.fixture(params=[p.name for p in SOURCE_CODE_DIRECTORY.iterdir()])
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
