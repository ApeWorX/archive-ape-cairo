# SPDX-License-Identifier: MIT
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin

@storage_var
func public_key() -> (res : felt):
end

@storage_var
func nonce() -> (res : felt):
end

@constructor
func constructor{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(pkey: felt):
    public_key.write(pkey)
    return ()
end

@view
func get_public_key{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }() -> (res: felt):
    let (res) = public_key.read()
    return (res=res)
end

@view
func get_nonce{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }() -> (res: felt):
    let (res) = nonce.read()
    return (res=res)
end

@external
func set_public_key{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(new_public_key: felt):
    public_key.write(new_public_key)
    return ()
end

@view
func is_valid_signature{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr,
        ecdsa_ptr: SignatureBuiltin*
    }(
        hash: felt,
        signature_len: felt,
        signature: felt*
    ) -> (is_valid: felt):
    return (is_valid=1)
end

@external
func __execute__{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr,
        ecdsa_ptr: SignatureBuiltin*
    }(
        call_array_len: felt,
        call_array: felt*,
        calldata_len: felt,
        calldata: felt*,
        nonce: felt
    ) -> (response_len: felt, response: felt*):
    let x: felt* = &[1]
    return (0, x)
end
