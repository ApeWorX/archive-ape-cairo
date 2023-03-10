#[contract]
mod Storage {
    #[view]
    fn supports_interface(interface_id: felt) -> bool {
        true
    }

    #[external]
    fn register_interface(interface_id: felt) {
    }
}
