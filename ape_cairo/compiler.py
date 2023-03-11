import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, cast

from ape.api import CompilerAPI, PluginConfig
from ape.exceptions import CompilerError, ConfigError
from ape.utils import get_relative_path
from eth_utils import to_hex
from ethpm_types import ContractType, PackageManifest
from pkg_resources import get_distribution
from semantic_version import Version  # type: ignore

STARKNET_COMPILE = "starknet-compile"
STARKNET_SIERRA_COMPILE = "starknet-sierra-compile"


class CairoConfig(PluginConfig):
    dependencies: List[str] = []
    manifest: Optional[str] = None


class CairoCompiler(CompilerAPI):
    @property
    def name(self) -> str:
        return "cairo"

    @property
    def manifest_path(self) -> Optional[Path]:
        if not self.config.manifest:
            return None

        return Path(self.config.manifest).expanduser().resolve()

    @property
    def config(self) -> CairoConfig:
        return cast(CairoConfig, self.config_manager.get_config("cairo"))

    @property
    def starknet_output_path(self) -> Path:
        return self.project_manager.local_project._cache_folder / "starknet"

    @property
    def casm_output_path(self) -> Path:
        return self.starknet_output_path / "casm"

    def starknet_compile(
        self,
        in_path: Path,
        out_path: Path,
        replace_ids: bool = False,
        allow_libfuncs_list_name: Optional[str] = None,
    ):
        _bin = self._which(STARKNET_COMPILE)
        arguments = [*_bin, str(in_path), str(out_path)]
        if replace_ids:
            arguments.append("--replace-ids")
        if allow_libfuncs_list_name is not None:
            arguments.extend(("--allowed-libfuncs-list-name", allow_libfuncs_list_name))

        self._compile(*arguments)

    def starknet_sierra_compile(
        self, in_path: Path, out_path: Path, allow_libfuncs_list_name: Optional[str] = None
    ):
        _bin = self._which(STARKNET_SIERRA_COMPILE)
        arguments = [*_bin, str(in_path), str(out_path)]
        if allow_libfuncs_list_name is not None:
            arguments.extend(("--allowed-libfuncs-list-name", allow_libfuncs_list_name))

        self._compile(*arguments)

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

        # Create all artifact directories (without assuming one is in another).
        self.starknet_output_path.mkdir(parents=True, exist_ok=True)
        self.casm_output_path.mkdir(parents=True, exist_ok=True)

        # search_paths = [base_path, *cached_paths_to_add]
        for contract_path in contract_filepaths:
            # Store the raw Starknet artifact itself.
            source_id = str(get_relative_path(contract_path, base_path))
            contract_name = source_id.replace(os.path.sep, ".").replace(".cairo", "")

            # Create Sierra contract classes.
            program_path = self.starknet_output_path / f"{contract_name}.json"
            program_path.unlink(missing_ok=True)
            self.starknet_compile(
                contract_path,
                program_path,
                replace_ids=True,
                allow_libfuncs_list_name="experimental_v0.1.0",
            )

            # Create Compiled contract classes.
            casm_path = self.casm_output_path / f"{contract_name}.casm"
            self.starknet_sierra_compile(
                program_path, casm_path, allow_libfuncs_list_name="experimental_v0.1.0"
            )

            output_dict = json.loads(program_path.read_text())
            contract_type = ContractType(
                abi=output_dict["abi"],
                contractName=contract_name,
                sourceId=source_id,
                runtimeBytecode={"bytecode": to_hex(text=program_path.read_text())},
                deploymentBytecode={"bytecode": to_hex(text=str(casm_path.read_text()))},
            )
            contract_types.append(contract_type)

        return contract_types

    def _compile(self, *args) -> bytes:
        popen = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = popen.communicate()
        if err:
            raise CompilerError(f"Failed to compile:\n{err.decode('utf8')}.")

        return output

    def _which(self, bin_name: str) -> List[str]:
        if self.manifest_path is not None:
            return [
                "cargo",
                "run" "--bin",
                bin_name,
                "--manifest-path",
                self.manifest_path.as_posix(),
            ]

        _bin = shutil.which(bin_name)
        if not _bin:
            raise CompilerError(
                f"`{STARKNET_COMPILE}` binary required in $PATH prior to compiling."
            )

        return [_bin]
