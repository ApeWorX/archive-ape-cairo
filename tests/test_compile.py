from pathlib import Path

from tests.conftest import SOURCE_CODE_DIRECTORY, SOURCE_FILES


def test_compile_all_files(compiler, project):
    source_files = [SOURCE_CODE_DIRECTORY / s for s in SOURCE_FILES]
    compiler.compile(source_files, base_path=SOURCE_CODE_DIRECTORY)
    for src_file in SOURCE_FILES:
        expected = get_expected_contract_type_name(src_file)
        assert project.get_contract(expected)
        assert getattr(project, expected)

    # Make sure can call compile twice
    compiler.compile(source_files, base_path=SOURCE_CODE_DIRECTORY)

    # Make sure can actually use dot-access
    assert project.namespace0.library
    assert project.namespace1.library


def test_compile_individual_files(compiler, contract, project):
    compiler.compile([contract], base_path=SOURCE_CODE_DIRECTORY)
    expected = get_expected_contract_type_name(contract)
    assert project.get_contract(expected)
    assert getattr(project, expected)

    # Make sure can call compile twice
    compiler.compile([contract], base_path=SOURCE_CODE_DIRECTORY)


def test_event_abi_migration(compiler):
    contract_with_event = SOURCE_CODE_DIRECTORY / "oz_proxy_lib.cairo"
    contract_type = compiler.compile([contract_with_event], base_path=SOURCE_CODE_DIRECTORY)[0]
    event_abi = [abi for abi in contract_type.abi if abi.type == "event"][0]
    assert len(event_abi.inputs) == 1
    assert event_abi.inputs[0].name == "implementation"
    assert event_abi.inputs[0].type == "felt"
    assert not event_abi.inputs[0].indexed


def get_expected_contract_type_name(contract_path: Path) -> str:
    """
    Converts paths like Path("path/to/base_dir/namespace/library.cairo") -> "namespace.library".
    """
    return (
        str(contract_path)
        .replace(str(SOURCE_CODE_DIRECTORY), "")
        .replace(".cairo", "")
        .strip("/")
        .replace("/", ".")
    )
