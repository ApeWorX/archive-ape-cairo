from pathlib import Path
from typing import List, Optional, Set

from ape.api import CompilerAPI
from ape.exceptions import CompilerError
from ape.utils import get_relative_path
from ethpm_types import ContractType
from pkg_resources import get_distribution  # type: ignore
from starknet_py.utils.compiler.starknet_compile import starknet_compile
from starkware.starknet.services.api.contract_definition import ContractDefinition  # type: ignore


class CairoCompiler(CompilerAPI):
    @property
    def name(self) -> str:
        return "cairo"

    def get_versions(self, all_paths: List[Path]) -> Set[str]:
        # NOTE: Currently, we are not doing anything with versions.
        return {get_distribution("cairo-lang").version}

    def compile(
        self, contract_filepaths: List[Path], base_path: Optional[Path]
    ) -> List[ContractType]:
        if not contract_filepaths:
            return []

        contract_types = []
        for contract_path in contract_filepaths:
            search_paths = [base_path] if base_path else []

            try:
                result_str = starknet_compile(contract_path.read_text(), search_paths=search_paths)
            except ValueError as err:
                raise CompilerError(f"Failed to compile '{contract_path.name}': {err}") from err

            definition = ContractDefinition.loads(result_str)

            contract_type_data = {
                "contractName": contract_path.stem,
                "sourceId": str(get_relative_path(contract_path, base_path)),
                "deploymentBytecode": {"bytecode": definition.serialize()},
                "runtimeBytecode": {"bytecode": definition.program.serialize()},
            }

            contract_type = ContractType.parse_obj(contract_type_data)
            contract_types.append(contract_type)

        return contract_types
