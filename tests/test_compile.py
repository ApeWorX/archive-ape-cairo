import shutil
from pathlib import Path

from tests.conftest import SOURCE_FILES


def test_compile_all_files(compiler, project):
    source_files = [project.contracts_folder / s for s in SOURCE_FILES]
    result = compiler.compile(source_files)
    assert len(result) == len(source_files)

    for src_file in SOURCE_FILES:
        expected = get_expected_contract_type_name(src_file, project.contracts_folder)
        assert project.get_contract(expected)
        assert getattr(project, expected)

    # Make sure can call compile twice
    compiler.compile(source_files)

    # Make sure can actually use dot-access
    assert project.namespace0.library
    assert project.namespace1.library


def test_compile_individual_files(compiler, contract, project):
    result = compiler.compile([contract])
    assert len(result) == 1
    expected = get_expected_contract_type_name(contract, project.contracts_folder)
    assert project.get_contract(expected)
    assert getattr(project, expected)

    # Make sure can call compile twice
    compiler.compile([contract])


def test_event_abi_migration(compiler, project):
    contract_with_event = project.contracts_folder / "openzeppelin" / "upgrades" / "library.cairo"
    contract_type = compiler.compile([contract_with_event])[0]
    event_abi = [abi for abi in contract_type.abi if abi.type == "event"][0]
    assert len(event_abi.inputs) == 1
    assert event_abi.inputs[0].name == "implementation"
    assert event_abi.inputs[0].type == "felt"
    assert not event_abi.inputs[0].indexed


def get_expected_contract_type_name(contract_path: Path, base_path: Path) -> str:
    """
    Converts paths like Path("path/to/base_dir/namespace/library.cairo") -> "namespace.library".
    """
    return (
        str(contract_path)
        .replace(str(base_path), "")
        .replace(".cairo", "")
        .strip("/")
        .replace("/", ".")
    )


def test_dependency(project, compiler):
    source_files = [project.contracts_folder / s for s in SOURCE_FILES]
    compiler.compile(source_files)
    dependency_path = project.config_manager.DATA_FOLDER / "packages" / "TestDependency"
    shutil.rmtree(dependency_path)

    # Tests against bug where would fail even though files are already in .cache and the
    # dependency manifest is not needed anymore.
    assert compiler.compile(source_files)
