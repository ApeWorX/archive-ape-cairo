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
    assert project.storage


def test_compile_individual_files(compiler, contract, project):
    result = compiler.compile([contract])
    assert len(result) == 1
    expected = get_expected_contract_type_name(contract, project.contracts_folder)
    assert project.get_contract(expected)
    assert getattr(project, expected)

    # Make sure can call compile twice
    compiler.compile([contract])


def test_event_abi_migration(compiler, project):
    contract_with_event = project.contracts_folder / "storage.cairo"
    contract_type = compiler.compile([contract_with_event])[0]
    event_abi = [abi for abi in contract_type.abi if abi.type == "event"][0]
    assert len(event_abi.inputs) == 1
    assert event_abi.inputs[0].name == "interface_id"
    assert event_abi.inputs[0].type == "core::felt252"
    assert not event_abi.inputs[0].indexed


def test_constructor(compiler, project):
    contract_with_event = project.contracts_folder / "storage.cairo"
    contract_type = compiler.compile([contract_with_event])[0]
    constructor = contract_type.constructor
    assert len(constructor.inputs) == 1


def get_expected_contract_type_name(contract_path: Path, base_path: Path) -> str:
    """
    Converts paths like Path("path/to/base_dir/namespace/storage.cairo") -> "namespace.storage".
    """
    return (
        str(contract_path)
        .replace(str(base_path), "")
        .replace(".cairo", "")
        .strip("/")
        .replace("/", ".")
    )


def test_get_versions(compiler, project):
    path = project.contracts_folder / "storage.cairo"
    versions = compiler.get_versions([path])
    assert versions == {"v1.0.0-alpha.7"}
