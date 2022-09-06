<<<<<<< HEAD
<<<<<<< HEAD
// NOTE: This contract is for test purposes only.
// Its intent is to provide a variety of ABI types to test against.
%lang starknet

// Make sure we can compile structs.
struct DependencyStruct {
    foo: felt,
    bar: felt,
}
=======
# NOTE: This contract is for test purposes only.
# Its intent is to provide a variety of ABI types to test against.
%lang starknet

# Make sure we can compile structs.
struct DependencyStruct:
    member foo : felt
    member bar : felt
end
>>>>>>> b71d4aa (feat: dependencies)
=======
// NOTE: This contract is for test purposes only.
// Its intent is to provide a variety of ABI types to test against.
%lang starknet

// Make sure we can compile structs.
struct DependencyStruct {
    foo: felt,
    bar: felt,
}
>>>>>>> 7dc57f9 (chore: uprade cairo lang)
