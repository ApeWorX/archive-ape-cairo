import ape


def test_compile(contract):
    ape.compilers.compile([contract])
    assert ape.project.get_contract(contract.stem)
