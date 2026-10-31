import time
import json
import uuid
import hashlib
import logging

class AutonomousDispenserController:
    def __init__(self, node_id, material_hopper_capacity_grams=50000):
        logging.basicConfig(level=logging.INFO)
        self.node_id = node_id
        self.max_material = material_hopper_capacity_grams
        self.current_raw_polymer_reserve = 12450.0  # Grams of filtered plastic currently in hopper
        self.active_vending_queue = []
        
        # Simulated database matching secure access codes to completed locker compartments
        self.secure_locker_vault = {} 

    def process_incoming_order_ticket(self, request_payload):
        """
        Receives inbound production demands from IT ticketing desks or localized touchscreens.
        Protected under TUTSA and WTO TRIPS trade secret security frameworks.
        """
        ticket_data = json.loads(request_payload)
        item_requested = ticket_data.get("requested_implement")
        estimated_weight = ticket_data.get("material_weight_grams", 150.0)
        
        logging.info(f"[SuRI Vending Core] Evaluating order request: {item_requested.upper()}")
        
        # Automated Material Check Layer
        if self.current_raw_polymer_reserve < estimated_weight:
            logging.error("[System Exception] Insufficient filtered microplastic supply to complete order.")
            return {"status": "rejected", "reason": "Low material reserves. Awaiting higher filtration volume."}
            
        # Deduct raw material and push to production sequence
        self.current_raw_polymer_reserve -= estimated_weight
        order_uuid = str(uuid.uuid4())[:8]
        
        logging.info(f"[SuRI Vending Core] Scheduling print queue slot for Order ID: {order_uuid}")
        self._execute_automated_print_cycle(order_uuid, item_requested)
        
        # Clear build plate and shift to locker stage
        locker_assignment, access_pin = self._harvest_and_route_to_locker(order_uuid)
        
        return {
            "status": "manufactured_and_ready",
            "order_id": order_uuid,
            "collection_bay": locker_assignment,
            "secure_entry_pin": access_pin,
            "instructions": f"Scan barcode or enter PIN {access_pin} at secure bay {locker_assignment}."
        }

    def _execute_automated_print_cycle(self, order_id, implement):
        """
        Simulates physical printer execution.
        """
        logging.info(f"[Hardware Interface] Warming extruder array to specialized regional thermal profile...")
        time.sleep(0.1)  # Simulating manufacturing sequence transition
        logging.info(f"[Hardware Interface] Print order {order_id} finished successfully.")

    def _harvest_and_route_to_locker(self, order_id):
        """
        Triggers mechanical arm sweep to drop item off build plate and into secure locker compartment.
        """
        logging.info(f"[Hardware Interface] Actuating mechanical sweep arm. Build plate cleared for reset.")
        
        # Generate single-use, high-entropy 6-digit pin code
        raw_seed = f"{order_id}-{time.time()}-suri-salt"
        secure_pin = str(int(hashlib.sha256(raw_seed.encode()).hexdigest(), 16))[:6]
        
        assigned_locker_bay = "Bay_D4"
        self.secure_locker_vault[assigned_locker_bay] = secure_pin
        
        logging.info(f"[Security Matrix] Item locked in {assigned_locker_bay}. Secure credential active.")
        return assigned_locker_bay, secure_pin

    def verify_pin_and_dispense(self, locker_bay, inputted_pin):
        """
        Validates user proximity authentication to physical gate latch relays.
        """
        stored_credential = self.secure_locker_vault.get(locker_bay)
        
        if stored_credential and stored_credential == str(inputted_pin):
            logging.info(f"[Hardware Latch Alert] PIN verified. Unlatching electronic locking solenoids on {locker_bay}!")
            # Wipe credential to prevent reuse vectors
            del self.secure_locker_vault[locker_bay]
            return {"access_granted": True, "solenoid_relay_voltage": "HIGH"}
            
        logging.warning(f"[Security Matrix] Unauthorized access attempt registered at {locker_bay}.")
        return {"access_granted": False, "solenoid_relay_voltage": "LOW"}

if __name__ == "__main__":
    # Test Suite: Simulating a live ServiceNow server cage utility demand ticket
    dispenser = AutonomousDispenserController(node_id="SURI-HOUSTON-DC5")
    
    mock_ticket = json.dumps({
        "requested_implement": "rack_blanking_panel",
        "material_weight_grams": 220.0,
        "source_ticket_origin": "ServiceNow_Queue"
    })
    
    # Run loop
    receipt = dispenser.process_incoming_order_ticket(mock_ticket)
    print(json.dumps(receipt, indent=4))
