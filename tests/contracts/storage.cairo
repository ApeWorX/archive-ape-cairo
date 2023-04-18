mod importme;

#[contract]
mod Storage {
    struct Storage {
        store_id: felt252
    }

    #[constructor]
    fn constructor(sid: felt252) {
        store_id::write(sid);
    }

    #[view]
    fn supports_interface(interface_id: felt252) -> bool {
        true
    }

    #[external]
    fn register_interface(interface_id: felt252) {
    }

    #[event]
    fn event_interface(interface_id: felt252){
    }
}
