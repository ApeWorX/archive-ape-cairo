use serde::Serde;
use starknet::ContractAddress;
use array::ArrayTrait;

struct Call {
    to: ContractAddress,
    selector: felt252,
    calldata: Array<felt252>
}

#[account_contract]
mod Account {
    use array::ArrayTrait;
    use super::Call;
    use super::ArrayCallSerde;
    use super::ArrayCallDrop;

    #[constructor]
    fn constructor(_public_key: felt252) {
    }

    // #[external]
    fn __execute__(mut calls: Array<Call>) -> Array<Span<felt252>> {
        let mut arr = ArrayTrait::new();
        return arr;
    }

    // #[external]
    fn __validate__(mut calls: Array<Call>) -> felt252 {
        0
    }

    #[external]
    fn __validate_declare__(class_hash: felt252) -> felt252 {
        0
    }

    #[external]
    fn __validate_deploy__(
        class_hash: felt252,
        contract_address_salt: felt252,
        _public_key: felt252
    ) -> felt252 {
        0
    }

    #[external]
    fn set_public_key(new_public_key: felt252) {
    }

    #[view]
    fn get_public_key() -> felt252 {
        0
    }

    // #[view]
    fn is_valid_signature(message: felt252, signature: Span<felt252>) -> u32 {
        0_u32
    }

    #[view]
    fn supports_interface(interface_id: u32) -> bool {
        true
    }
}

impl ArrayCallDrop of Drop::<Array<Call>>;

impl CallSerde of Serde::<Call> {
    fn serialize(ref output: Array<felt252>, input: Call) {
        let Call{to, selector, calldata } = input;
        Serde::serialize(ref output, to);
        Serde::serialize(ref output, selector);
        Serde::serialize(ref output, calldata);
    }

    fn deserialize(ref serialized: Span<felt252>) -> Option<Call> {
        let to = Serde::<ContractAddress>::deserialize(ref serialized)?;
        let selector = Serde::<felt252>::deserialize(ref serialized)?;
        let calldata = Serde::<Array::<felt252>>::deserialize(ref serialized)?;
        Option::Some(Call { to, selector, calldata })
    }
}

impl ArrayCallSerde of Serde::<Array<Call>> {
    fn serialize(ref output: Array<felt252>, mut input: Array<Call>) {
    }

    fn deserialize(ref serialized: Span<felt252>) -> Option<Array<Call>> {
        let mut arr = ArrayTrait::new();
        return Option::Some(arr);
    }
}
