from pathlib import Path
from typing import List, Optional, Set

from ape.api import CompilerAPI, PluginConfig
from ape.exceptions import CompilerError, ConfigError
from ape.utils import get_relative_path
from ethpm_types import ContractType, PackageManifest
from pkg_resources import get_distribution  # type: ignore
from starknet_py.compile.compiler import StarknetCompilationSource, starknet_compile  # type: ignore
from starkware.starknet.services.api.contract_class import ContractClass  # type: ignore


class CairoConfig(PluginConfig):
    dependencies: List[str] = []


def _has_execute_method(contract_path: Path) -> bool:
    content = Path(contract_path).read_text(encoding="utf-8")
    return any(line.startswith("func __execute__{") for line in content.splitlines())


class CairoCompiler(CompilerAPI):
    @property
    def name(self) -> str:
        return "cairo"

    @property
    def config(self) -> CairoConfig:
        return self.config_manager.get_config("cairo")  # type: ignore

    def load_dependencies(self, base_path: Optional[Path] = None):
        _ = self.project_manager.dependencies
        contracts_path = base_path or self.config_manager.contracts_folder
        packages_folder = self.config_manager.packages_folder

        for dependency_item in self.config.dependencies:
            if "@" not in dependency_item:
                dependency_name = dependency_item
                version = None
            else:
                dependency_name, version = dependency_item.split("@")

            dependency_package_folder = packages_folder / dependency_name
            if version is None and dependency_package_folder.is_dir():
                version_options = [d for d in dependency_package_folder.iterdir() if d.is_dir()]
                if not version_options:
                    raise ConfigError(f"No versions found for dependency '{dependency_name}'.")

                elif len(version_options) != 1:
                    raise ConfigError(
                        f"Ambiguous dependency version for '{dependency_name}'. "
                        f"Use 'name@version' syntax to clarify."
                    )

                version = version_options[0].name

            if version and version[0].isnumeric():
                version = f"v{version}"

            version = version or ""  # For mypy
            source_manifest_path = (
                packages_folder / dependency_name / version / f"{dependency_name}.json"
            )
            source_manifest = PackageManifest.parse_raw(source_manifest_path.read_text())
            destination_base_path = contracts_path / ".cache" / dependency_name / version

            if dependency_name not in [d.name for d in self.config_manager.dependencies]:
                raise ConfigError(f"Dependency '{dependency_item}' not configured.")

            sources = source_manifest.sources or {}
            for source_id, source in sources.items():
                suffix = Path(f"{source_id.replace('.cairo', '').replace('.', '/')}.cairo")
                destination_path = destination_base_path / suffix

                if destination_path.is_file():
                    continue

                if source.content:
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    destination_path.touch()
                    destination_path.write_text(source.content)

    def get_versions(self, all_paths: List[Path]) -> Set[str]:
        # NOTE: Currently, we are not doing anything with versions.
        return {get_distribution("cairo-lang").version}

    def compile(
        self, contract_filepaths: List[Path], base_path: Optional[Path] = None
    ) -> List[ContractType]:
        contracts_path = base_path or self.project_manager.contracts_folder

        # NOTE: still load dependencies even if no contacts in project.
        self.load_dependencies()

        if not contract_filepaths:
            return []

        contract_types = []
        base_cache_path = contracts_path / ".cache"
        cached_paths_to_add = []
        if base_cache_path.is_dir():
            dependency_folders = (
                [base_cache_path / p for p in base_cache_path.iterdir() if p.is_dir()]
                if base_cache_path.is_dir()
                else []
            )
            for dependency_folder in dependency_folders:
                cached_paths_to_add.extend(
                    [dependency_folder / p for p in dependency_folder.iterdir() if p.is_dir()]
                )

        search_paths = [contracts_path, *cached_paths_to_add]
        for contract_path in contract_filepaths:
            try:
                source = StarknetCompilationSource(str(contract_path))
                is_account = _has_execute_method(contract_path)
                result_str = starknet_compile(
                    [source], search_paths=search_paths, is_account_contract=is_account
                )
            except ValueError as err:
                raise CompilerError(f"Failed to compile '{contract_path.name}': {err}") from err

            definition = ContractClass.loads(result_str)

            # Change events' 'data' field to 'inputs'
            for abi in definition.abi:
                if abi["type"] == "event" and "data" in abi:
                    abi["inputs"] = abi.pop("data")

            source_id = str(get_relative_path(contract_path, contracts_path))
            contract_name = source_id.replace(".cairo", "").replace("/", ".")
            contract_type_data = {
                "contractName": contract_name,
                "sourceId": source_id,
                "deploymentBytecode": {"bytecode": definition.serialize().hex()},
                "runtimeBytecode": {},
                "abi": definition.abi,
            }

            contract_type = ContractType.parse_obj(contract_type_data)
            contract_types.append(contract_type)

        return contract_types
