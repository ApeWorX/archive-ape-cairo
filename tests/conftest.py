import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import mkdtemp

import ape
import pytest
from ape.utils import get_all_files_in_directory

# NOTE: Ensure that we don't use local paths for these
ape.config.DATA_FOLDER = Path(mkdtemp()).resolve()
ape.config.PROJECT_FOLDER = Path(mkdtemp()).resolve()


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


@pytest.fixture
def config():
    return ape.config


@pytest.fixture
def project(config):
    caches = (
        PROJECT_DIRECTORY / ".build",
        SOURCE_CODE_DIRECTORY / ".cache",
        DEPENDENCY_DIRECTORY / ".build",
        DEPENDENCY_SOURCE_CODE_DIRECTORY / ".cache",
    )
    for cache in caches:
        if cache.is_dir():
            shutil.rmtree(cache)

    project_dest_dir = config.PROJECT_FOLDER / PROJECT_DIRECTORY.name
    copy_tree(str(PROJECT_DIRECTORY.as_posix()), str(project_dest_dir))
    with config.using_project(project_dest_dir) as project:
        yield project
        if project.local_project._cache_folder.is_dir():
            shutil.rmtree(project.local_project._cache_folder)


# NOTE: Params converted to strings to looks nicer in pytest case outputs
@pytest.fixture(params=[str(p) for p in SOURCE_FILES])
def contract(request, project):
    yield (project.contracts_folder / request.param).absolute()


@pytest.fixture
def compiler():
    return ape.compilers.registered_compilers[".cairo"]
