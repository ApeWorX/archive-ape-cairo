from tests.conftest import SOURCE_CODE_DIRECTORY


def test_compile(compiler, contract, project):
    compiler.compile([contract], base_path=SOURCE_CODE_DIRECTORY)
    assert project.get_contract(contract.stem)


def test_event_abi_migration(compiler):
    contract_with_event = SOURCE_CODE_DIRECTORY / "oz_proxy_lib.cairo"
    contract_type = compiler.compile([contract_with_event], base_path=SOURCE_CODE_DIRECTORY)[0]
    event_abi = [abi for abi in contract_type.abi if abi.type == "event"][0]
    assert len(event_abi.inputs) == 1
    assert event_abi.inputs[0].name == "implementation"
    assert event_abi.inputs[0].type == "felt"
    assert not event_abi.inputs[0].indexed
