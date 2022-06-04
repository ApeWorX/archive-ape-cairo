import os
import shutil
from pathlib import Path

import ape
import pytest
from ape.utils import get_all_files_in_directory

PROJECT_DIRECTORY = Path(__file__).parent
SOURCE_CODE_DIRECTORY = PROJECT_DIRECTORY / "contracts"
DEPENDENCY_DIRECTORY = PROJECT_DIRECTORY / "dependency"
DEPENDENCY_SOURCE_CODE_DIRECTORY = DEPENDENCY_DIRECTORY / "src"

SOURCE_FILES = [
    p
    for p in [
        Path(str(p).replace(str(SOURCE_CODE_DIRECTORY), "").strip("/"))
        for p in get_all_files_in_directory(SOURCE_CODE_DIRECTORY)
    ]
    if not str(p).startswith(".cache")
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
    caches = (
        PROJECT_DIRECTORY / ".build",
        SOURCE_CODE_DIRECTORY / ".caches",
        DEPENDENCY_DIRECTORY / ".build",
        DEPENDENCY_SOURCE_CODE_DIRECTORY / ".cache",
    )

    def clean():
        for cache_dir in caches:
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)

    clean()
    yield
    clean()


@pytest.fixture
def project():
    return ape.project


@pytest.fixture
def compiler():
    return ape.compilers.registered_compilers[".cairo"]
