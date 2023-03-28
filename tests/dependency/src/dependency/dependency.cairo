#[contract]
mod Dependency {
    #[view]
    fn dep_view(interface_id: felt252) -> bool {
        true
    }

    #[external]
    fn dep_extern(interface_id: felt252) {
    }
}
