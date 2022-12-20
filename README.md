# Quick Start

Ape compiler plugin around [the Cairo language](https://github.com/starkware-libs/cairo-lang).

## Dependencies

* [python3](https://www.python.org/downloads) version 3.8 or greater, python3-dev

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

## **Questions / FAQ**

Questions are welcome! If you have any questions regarding ApeWorX, feel free to ask them using [Newton](https://www.newton.so/?tags=ape).

### **FAQ**

- [Why am I getting the error message "ArgumentsLengthError"?](https://www.newton.so/view/63a0a2ee5e3e06d5a48065c5)

- [Why am I getting an "account \_\_execute\_\_" error message?](https://www.newton.so/view/63a0a28e1599f98884ef31fb)

- [Why am I having trouble deploying my Cairo contract?](https://www.newton.so/view/63a0a2455e3e06d5a48065c1)

- [How can I test on multi-chain with both Starknet and Ethereum?](https://www.newton.so/view/63a09b04bcc5e0167be127e5)

- [Using ape starknet accounts list](https://www.newton.so/view/63a09ad4bcc5e0167be127e3)

- [How do I call an account while trying to test a function?](https://www.newton.so/view/63a09969deac7f54af6b0f92)

- [Why do I need to fund a Starknet account before deploying it?](https://www.newton.so/view/63a09933bcc5e0167be127e1)

- [How do I fund newly created accounts from the ape console?](https://www.newton.so/view/63a097a19edbdf54f701c406)

- [Why are the cairo and starknet plugins not installing properly?](https://www.newton.so/view/63a096fc9edbdf54f701c405)
