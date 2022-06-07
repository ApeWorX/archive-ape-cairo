# Ape Cairo

Ape compiler plugin around [the Cairo language](https://github.com/starkware-libs/cairo-lang).

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-cairo
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/<PYPI_NAME>.git
cd ape-cairo
python3 setup.py install
```

## Quick Usage

In a project directory where there are `.cairo` files in your `contracts/` directory, run the `compile` command:

```bash
ape compile
```

### Configure Dependencies

You can configure dependencies, such as from `GitHub`, using your `ape-config.yaml` file.

There are two things you need to add:

1. Add your dependency to Ape's root `dependencies:` key to trigger downloading and compiling it.
2. Configure the `ape-cairo` plugin to load that dependency in your project.

For more information on dependencies, [see this guide](https://docs.apeworx.io/ape/stable/userguides/config.html#dependencies).

Your resulting `ape-config.yaml` will look something like:

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

## License

This project is licensed under the [Apache 2.0](LICENSE).
