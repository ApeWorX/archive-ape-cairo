# Quick Start

Ape compiler plugin around [the Cairo language](https://github.com/starkware-libs/cairo-lang).

## Dependencies

- [python3](https://www.python.org/downloads) version 3.8 or greater, python3-dev
- [Rust](https://www.rust-lang.org/)

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-cairo
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-cairo.git
cd ape-cairo
python3 setup.py install
```

## Quick Usage

First, you will need to tell `ape-cairo` how to use the Cairo compiler.
There are two ways to do this:

1. Configure your Cairo manifest path in your `ape-config.yaml`.
2. Build or add Cairo compiler binaries to your $PATH.

Both options require cloning the Cairo compiler source code:

```sh
git clone git@github.com:starkware-libs/cairo.git
cd cairo
git fetch --all
git checkout <tag>  # e.g. v1.0.0-alpha.6
```

To do the first option, add the following to your `ape-config.yaml` file:

```yaml
cairo:
  manifest: /Users/home/path/to/cairo/Cargo.toml
```

Now, when compiling, Ape will use the command `cargo run --bin <BIN> --manifest-path <CAIRO-MANIFEST>`.
To do the second option instead, build the release binaries for your OS:

```sh
cargo build --release
```

**NOTE**: This requires being in the same directory as Cairo.

After the build completes, add the target path to your global $PATH variable.
(You may want to add this to your `.zshrc` / `.bashrc` file):

```sh
export PATH=$PATH:$HOME/path/to/cairo/target/release
```

Verify you have `sierra-compile` in your `$PATH` by doing:

```bash
which sierra-compile
```

**WARN**: Note that when using Cairo-lang the python package, it will add conflicting binaries with the same name.
You will need to ensure you are using the correct binaries if you have `cairo-lang` the Python package installed.

```shell
which starknet-compile
```

Alternatively, the first approach avoids this problem.

### Using the Compiler

In a project directory where there are `.cairo` files in your `contracts/` directory, run the `compile` command:

```bash
ape compile
```

It should create `ContractType` objects in your `.build/` folder containing the necessary Sierra code for contract declaration.

### Configure Dependencies

You can configure dependencies, such as from `GitHub`, using your `ape-config.yaml` file.

There are two things you need to add:

1. Add your dependency to Ape's root `dependencies:` key to trigger downloading and compiling it.
2. Configure the `ape-cairo` plugin to load that dependency in your project.

For more information on dependencies, [see this guide](https://docs.apeworx.io/ape/stable/userguides/config.html#dependencies).

Your `ape-config.yaml` will look something like:

```yaml
dependencies:
  - name: OpenZeppelinCairo
    github: OpenZeppelin/cairo-contracts
    version: 0.1.0
    contracts_folder: src

cairo:
  dependencies:
    - OpenZeppelinCairo@0.1.0
```

**NOTE**: We are changing the `contracts/` folder to be `src` for this dependency.

Now, in my `contracts/` folder, I can import from `openzeppelin`:

```cairo
from openzeppelin.token.erc20.library import (
    ERC20_name,
    ERC20_symbol,
    ERC20_totalSupply,
    ERC20_decimals,
    ERC20_balanceOf,
    ERC20_allowance,
    ERC20_mint,
    ERC20_burn,
    ERC20_initializer,
    ERC20_approve,
    ERC20_increaseAllowance,
    ERC20_decreaseAllowance,
    ERC20_transfer,
    ERC20_transferFrom
)
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.
