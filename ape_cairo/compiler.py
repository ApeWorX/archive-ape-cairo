import json
import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional, Set, cast

from ape.api import CompilerAPI, PluginConfig
from ape.exceptions import CompilerError, ConfigError
from ape.utils import get_relative_path
from eth_utils import to_hex
from ethpm_types import ContractType, PackageManifest
from pkg_resources import get_distribution
from semantic_version import Version  # type: ignore


def _has_account_methods(contract_path: Path) -> bool:
    content = Path(contract_path).read_text(encoding="utf-8")
    lines = content.splitlines()
    has_execute = any(line.startswith("fn __execute__(") for line in lines)
    has_validate = any(line.startswith("fn __validate__(") for line in lines)
    has_validate_execute = any(line.startswith("fn __validate_declare__(") for line in lines)
    return has_execute and has_validate and has_validate_execute


class CairoConfig(PluginConfig):
    dependencies: List[str] = []


class CairoCompiler(CompilerAPI):
    @property
    def name(self) -> str:
        return "cairo"

    @property
    def config(self) -> CairoConfig:
        return cast(CairoConfig, self.config_manager.get_config("cairo"))

    @property
    def bin_name(self) -> str:
        return "starknet-compile"

    @cached_property
    def bin(self) -> str:
        path = shutil.which(self.bin_name)
        if not path:
            raise CompilerError(f"`{self.bin_name}` binary required in $PATH prior to compiling.")

        return path

    @property
    def sierra_output_path(self) -> Path:
        return self.project_manager.local_project._cache_folder / "sierra"

    def get_compiler_settings(
        self, contract_filepaths: List[Path], base_path: Optional[Path] = None
    ) -> Dict[Version, Dict]:
        settings: Dict[Version, Dict] = {}
        for version in self.get_versions(contract_filepaths):
            if version in settings:
                continue

            settings[version] = {}

        return settings

    def load_dependencies(self, base_path: Optional[Path] = None):
        deps = self.project_manager.dependencies

        # Have to re-exact manifests for some reason, maybe because of a bug
        # in tempfiles. This only affects tests; real projects don't need
        # this code. I am not sure why. Suddenly, the package just doesn't
        # exist anymore.
        for version_map in deps.values():
            for dep in version_map.values():
                dep.extract_manifest()

        base_path = base_path or self.config_manager.contracts_folder
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
            source_manifest_path = packages_folder / dependency_name

            if not source_manifest_path.is_dir():
                raise CompilerError(
                    f"Missing dependency '{dependency_name}' from packages {source_manifest_path}."
                )

            source_manifest_path = source_manifest_path / version / f"{dependency_name}.json"
            destination_base_path = base_path / ".cache" / dependency_name / version
            if destination_base_path.is_dir() and not source_manifest_path.is_file():
                # If the cache already exists and there is no dependency manifest file,
                # assume the cache was created via some other means and skip validation.
                continue

            elif not source_manifest_path.is_file():
                raise CompilerError(f"Dependency '{dependency_name}={version}' missing.")

            source_manifest = PackageManifest.parse_raw(source_manifest_path.read_text())

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
        base_path = base_path or self.project_manager.contracts_folder

        # NOTE: still load dependencies even if no contacts in project.
        self.load_dependencies()

        if not contract_filepaths:
            return []

        contract_types: List[ContractType] = []
        base_cache_path = base_path / ".cache"

        cached_paths_to_add = []
        dependency_folders = (
            [base_cache_path / p for p in base_cache_path.iterdir() if p.is_dir()]
            if base_cache_path.is_dir()
            else []
        )
        for dependency_folder in dependency_folders:
            cached_paths_to_add.extend(
                [dependency_folder / p for p in dependency_folder.iterdir() if p.is_dir()]
            )

        self.sierra_output_path.mkdir(parents=True, exist_ok=True)
        # search_paths = [base_path, *cached_paths_to_add]
        for contract_path in contract_filepaths:
            popen = subprocess.Popen(
                [
                    self.bin,
                    str(contract_path),
                    "--replace-ids",
                    "--allowed-libfuncs-list-name",
                    "experimental_v0.1.0",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, err = popen.communicate()
            if err:
                raise CompilerError(f"Failed to compile '{contract_path}':\n{err.decode('utf8')}.")

            output_str = output.decode("utf8")
            output_dict = json.loads(output_str)
            source_id = str(get_relative_path(contract_path, base_path))
            contract_name = source_id.replace(os.path.sep, ".").replace(".cairo", "")

            # Write out the Sierra program path.
            # The ContractType represents a link to this artifact.
            sierra_program_path = self.sierra_output_path / f"{contract_name}.txt"
            sierra_program_path.unlink(missing_ok=True)
            sierra_program_path.touch()
            sierra_program_path.write_text("\n".join(output_dict["sierra_program"]))

            # TODO: Research what is `sierra_program_debug_info`

            contract_type = ContractType(
                abi=output_dict["abi"],
                contractName=contract_name,
                sourceId=source_id,
                deploymentBytecode={"bytecode": to_hex(text=contract_name)},
            )
            contract_types.append(contract_type)

        return contract_types
