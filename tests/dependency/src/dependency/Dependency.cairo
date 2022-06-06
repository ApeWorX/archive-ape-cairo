# NOTE: This contract is for test purposes only.
# Its intent is to provide a variety of ABI types to test against.
%lang starknet

# Make sure we can compile structs.
struct DependencyStruct:
    member foo : felt
    member bar : felt
end
