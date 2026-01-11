from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Callable
import random
import heapq
import numpy as np

from medguard.data.generators.movements import dispense, expiry_withdraw, restock
from medguard.data.generators.inventory import generate_inventory
from medguard.data.generators.medications import generate_medications
from medguard.data.generators.brands import generate_brands
from medguard.data.generators.batches import generate_batches
from medguard.data.generators.companies import generate_companies
from medguard.data.generators.facilities import generate_facilities
from medguard.detection.events import generate_events
from medguard.detection.anomalies import generate_anomalies


START_TIME = datetime(2026, 1, 3, 0, 0, 0)
END_TIME = datetime(2026, 1, 7, 0, 0, 0)
TIME_STEP = timedelta(hours=1)

FACILITY_OPEN_HOUR = 8
FACILITY_CLOSE_HOUR = 18
AGENT_CYCLE_HOURS = 4


# event queue
class EventQueue:
    """priority queue for simulation events."""

    def __init__(self):
        self.heap = []
        self.counter = 0  # tie breaker for same timestamps

    def push(self, time: datetime, event_type: str, data: Dict):
        heapq.heappush(self.heap, (time, self.counter, event_type, data))
        self.counter += 1

    def pop(self):
        if self.heap:
            time, _, event_type, data = heapq.heappop(self.heap)
            return time, event_type, data
        return None

    def peek_time(self):
        if self.heap:
            return self.heap[0][0]
        return None

    def is_empty(self):
        return len(self.heap) == 0


rng = np.random.default_rng(seed=42)


# helper functions
# for purpose of demo, assume all facilities close by 6pm
def is_facility_open(hour: int) -> bool:
    """func to check if facilities are open"""
    return FACILITY_OPEN_HOUR <= hour < FACILITY_CLOSE_HOUR


def calculate_dispense_quantity(medication: Dict, facility_type: str) -> int:
    """
    Calculate realistic dispense quantity based on:
    - Medication base demand
    - Facility type (teaching hospitals dispense more)
    - Random variation (Poisson distribution)
    """
    base_demand = medication["base_demand"]
    # divide by 30 to get monthly and by 10 for 10 hour working period
    hourly_demand = base_demand / 30 / 10

    multipliers = {
        "TEACHING_HOSPITAL": 2.0,
        "GENERAL_HOSPITAL": 1.5,
        "COMMUNITY_PHARMACY": 1.0,
        "PRIMARY_HEALTH_CENTER": 0.5,
    }
    multiplier = multipliers.get(facility_type, 1.0)

    # poisson distribution for realistic variation
    expected = hourly_demand * multiplier
    return int(rng.poisson(expected)) if expected > 0.1 else 0


def calculate_restock_quantity(inventory: Dict) -> int:
    """how much to restock."""
    return inventory["reorder_point"] * 2


# simulation engine
class SimulationEngine:
    def __init__(
        self,
        inventory: List[Dict],
        medications: List[Dict],
        facilities: List[Dict],
        batches: List[Dict],
        start_time: datetime,
        end_time: datetime,
    ):
        self.inventory = inventory
        self.medications = medications
        self.facilities = facilities
        self.batches = batches
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time

        # Lookups
        self.med_lookup = {m["med_id"]: m for m in medications}
        self.facility_lookup = {f["facility_id"]: f for f in facilities}
        self.inventory_lookup = {inv["inventory_id"]: inv for inv in inventory}
        self.inventory_by_facility_med = defaultdict(list)
        for inv in inventory:
            key = (inv["facility_id"], inv["med_id"])
            self.inventory_by_facility_med[key].append(inv)

        # Event queue
        self.event_queue = EventQueue()

        # Logs
        self.movements_log: List[Dict] = []
        self.events_log: List[Dict] = []
        self.anomalies_log: List[Dict] = []

        # Tracking
        self.restocked_inventory = set()  # Prevent duplicate restocks
        self.last_agent_cycle = None

    def initialize(self):
        """Set up initial state and schedule initial events."""
        # print("starting simulation...")

        # seed initial receipts

        facility_offsets = {}

        for inv in self.inventory:
            if inv["quantity"] > 0:
                fac_id = inv["facility_id"]

            # 1% chance of skiping receipt to create ghost stock
            if random.random() < 0.01:
                continue  # no receipt, ghost stock

            # each facility gets receipts on a different day
            if fac_id not in facility_offsets:
                facility_offsets[fac_id] = len(facility_offsets) % 7

            offset_days = facility_offsets[fac_id]
            receipt_time = (
                self.start_time - timedelta(days=7) + timedelta(days=offset_days)
            )

            mov = restock(
                inventory=inv,
                quantity=inv["quantity"],
                timestamp=receipt_time,
                source="INITIAL_SEED",
            )
            self.movements_log.append(mov)

        #  hourly ticks schedule
        current = self.start_time
        while current < self.end_time:
            self.event_queue.push(current, "HOURLY_TICK", {})
            current += timedelta(hours=1)

        # agent cycles
        current = self.start_time
        while current < self.end_time:
            self.event_queue.push(current, "AGENT_CYCLE", {})
            current += timedelta(hours=AGENT_CYCLE_HOURS)

        # 4. Schedule demo scenarios (injected anomalies)
        self._schedule_demo_scenarios()

        # print(f"Scheduled {self.event_queue.counter} events")

    def _schedule_demo_scenarios(self):
        """
        Inject specific scenarios at known times for demo purposes.
        """
        # Scenario 1: geographic impossibility at hour 15
        self.event_queue.push(
            self.start_time + timedelta(hours=15),
            "INJECT_GEOGRAPHIC_ANOMALY",
            {"description": "Counterfeit batch appears in distant locations"},
        )

        # Scenario 2: geographic anomaly at hour 35
        self.event_queue.push(
            self.start_time + timedelta(hours=35),
            "INJECT_GEOGRAPHIC_ANOMALY",
            {"description": "Second counterfeit batch detected"},
        )

        # Scenario 3: impossible quantity at hour 50
        self.event_queue.push(
            self.start_time + timedelta(hours=50),
            "INJECT_IMPOSSIBLE_QUANTITY",
            {"description": "Batch dispensed more than existed"},
        )

    def run(self):
        """Main simulation loop."""

        while not self.event_queue.is_empty():
            event_time, event_type, event_data = self.event_queue.pop()

            if event_time >= self.end_time:
                break

            self.current_time = event_time
            self._process_event(event_type, event_data)

        # print(f"Movements: {len(self.movements_log)}")
        # print(f"Events: {len(self.events_log)}")
        # print(f"Anomalies: {len(self.anomalies_log)}")

        return {
            "final_inventory": self.inventory,
            "movements": self.movements_log,
            "events": self.events_log,
            "anomalies": self.anomalies_log,
            "simulation_start": self.start_time,
            "simulation_end": self.end_time,
        }

    def _process_event(self, event_type: str, event_data: Dict):
        """Route event to appropriate handler."""
        handlers = {
            "HOURLY_TICK": self._handle_hourly_tick,
            "AGENT_CYCLE": self._handle_agent_cycle,
            "INJECT_GEOGRAPHIC_ANOMALY": self._handle_inject_geographic,
            "INJECT_IMPOSSIBLE_QUANTITY": self._handle_inject_impossible_qty,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event_data)

    def _handle_hourly_tick(self, data: Dict):
        """Process one hour of simulation."""
        hour = self.current_time.hour

        # process expiry withdrawals
        self._process_expiry()

        # process dispensing - only during open hours
        if is_facility_open(hour):
            self._process_dispensing()

    def _process_expiry(self):
        """Remove expired stock from inventory."""
        for inv in self.inventory:
            if inv["quantity"] <= 0:
                continue

            expiry_date = datetime.strptime(inv["expiry_date"], "%Y-%m-%d")
            if self.current_time >= expiry_date:
                mov = expiry_withdraw(
                    inventory=inv,
                    quantity=inv["quantity"],
                    timestamp=self.current_time,
                    source="SIMULATION",
                )
                self.movements_log.append(mov)

    def _process_dispensing(self):
        """
        Process dispensing for all facilities.
        Quantity varies by medication demand and facility type.
        """
        for facility in self.facilities:
            facility_id = facility["facility_id"]
            facility_type = facility["facility_type"]

            # all inventory for this facility
            for inv in self.inventory:
                if inv["facility_id"] != facility_id:
                    continue
                if inv["quantity"] <= 0:
                    continue

                # medication info
                med = self.med_lookup.get(inv["med_id"])
                if not med:
                    continue

                # calculate dispense quantity
                qty = calculate_dispense_quantity(med, facility_type)

                if qty <= 0:
                    continue

                qty = min(
                    qty, inv["quantity"]
                )  # to prevent dispensing more than available

                # create dispense movement
                mov = dispense(
                    inventory=inv,
                    quantity=qty,
                    timestamp=self.current_time,
                    source="SIMULATION",
                    reason="PATIENT_DEMAND",
                )
                self.movements_log.append(mov)

    def _handle_agent_cycle(self, data: Dict):
        """
        Agent wakes up to:
        1. Detect events
        2. Process restocks
        3. Detect anomalies
        """
        # print(f"[Agent Cycle] {self.current_time}")

        #  generate events
        daily_events = generate_events(
            inventory=self.inventory,
            movements=self.movements_log,
            medications=self.medications,
            current_time=self.current_time,
            existing_events=self.events_log,
        )
        self.events_log.extend(daily_events)

        # process restocks: response to low stock
        self._process_restocks(daily_events)

        # detect anomalies
        new_anomalies = generate_anomalies(
            inventory=self.inventory,
            movements=self.movements_log,
            events=daily_events,
            facilities=self.facilities,
            batches=self.batches,
            current_time=self.current_time,
            existing_anomalies=self.anomalies_log,
        )
        self.anomalies_log.extend(new_anomalies)

        if new_anomalies:
            # replace print with actual agent logic
            print(f"Detected {len(new_anomalies)} new anomalies")
            for a in new_anomalies:
                print(f"{a['anomaly_type']}: {a['details'][:50]}...")

    def _process_restocks(self, events: List[Dict]):
        """Process restocks in response to low stock events."""
        low_stock_events = [e for e in events if e["event_type"] == "LOW_STOCK"]
        restock_count = 0
        for event in low_stock_events:
            inv_key = (event["facility_id"], event["med_id"])

            if inv_key in self.restocked_inventory:
                continue

            # find inventory
            inv = next(
                (
                    i
                    for i in self.inventory
                    if i["facility_id"] == event["facility_id"]
                    and i["med_id"] == event["med_id"]
                ),
                None,
            )

            if not inv or inv["quantity"] >= inv["reorder_point"]:
                continue

            # count as restocked
            self.restocked_inventory.add(inv_key)

            # put time between restock
            restock_time = self.current_time + timedelta(minutes=restock_count * 30)
            restock_count += 1

            # create restock
            qty = calculate_restock_quantity(inv)
            mov = restock(
                inventory=inv,
                quantity=qty,
                timestamp=restock_time,
                source="SIMULATION",
            )
            self.movements_log.append(mov)

    def _handle_inject_geographic(self, data: Dict):
        """Inject a geographic impossibility anomaly."""
        print(f"[Inject] Geographic anomaly at {self.current_time}")

        # random batch that has inventory
        batches_with_inventory = [
            inv["batch_id"] for inv in self.inventory if inv["quantity"] > 0
        ]
        if not batches_with_inventory:
            return

        batch_id = random.choice(batches_with_inventory)

        # which facility has the batch?
        source_inv = next(
            (
                inv
                for inv in self.inventory
                if inv["batch_id"] == batch_id and inv["quantity"] > 0
            ),
            None,
        )
        if not source_inv:
            return

        source_facility = self.facility_lookup.get(source_inv["facility_id"])
        if not source_facility:
            return

        # distant facility (different state)
        distant_facilities = [
            f for f in self.facilities if f["state"] != source_facility["state"]
        ]
        if not distant_facilities:
            return

        distant = random.choice(distant_facilities)

        # create a restock at the source
        mov1 = {
            "movement_id": f"MOV_{random.randint(100000, 999999)}",
            "inventory_id": source_inv["inventory_id"],
            "facility_id": source_inv["facility_id"],
            "batch_id": batch_id,
            "med_id": source_inv["med_id"],
            "movement_type": "RESTOCK",
            "quantity_change": 50,
            "quantity_after": source_inv["quantity"] + 50,
            "timestamp": self.current_time.isoformat(),
            "reference_id": "ANOMALY_INJECT",
            "source": "SIMULATION_ANOMALY",
            "reason": "GEOGRAPHIC_TEST",
        }
        self.movements_log.append(mov1)

        # create a restock at distant facility 1-2 hours later
        mov2 = {
            "movement_id": f"MOV_{random.randint(100000, 999999)}",
            "inventory_id": f"ANOMALY_{source_inv['inventory_id']}",
            "facility_id": distant["facility_id"],
            "batch_id": batch_id,  # same batch id
            "med_id": source_inv["med_id"],
            "movement_type": "RESTOCK",
            "quantity_change": random.randint(50, 150),
            "quantity_after": random.randint(50, 150),
            "timestamp": (
                self.current_time + timedelta(hours=random.randint(1, 2))
            ).isoformat(),
            "reference_id": "ANOMALY_INJECT",
            "source": "SIMULATION_ANOMALY",
            "reason": "GEOGRAPHIC_TEST",
        }
        self.movements_log.append(mov2)

        print(
            f"Injected: Batch {batch_id} at {source_facility['state']} and {distant['state']}"
        )

    def _handle_inject_impossible_qty(self, data: Dict):
        """Inject an impossible quantity anomaly."""
        print(f"[Inject] Impossible quantity at {self.current_time}")

        # pick a batch
        if not self.batches:
            return

        batch = random.choice(self.batches)
        batch_id = batch["batch_id"]
        initial_qty = batch["initial_quantity"]

        # which facility has the batch?
        inv = next((i for i in self.inventory if i["batch_id"] == batch_id), None)
        if not inv:
            return

        # Create dispenses that exceed initial quantity
        excess_qty = initial_qty * 12

        for i in range(5):
            mov = {
                "movement_id": f"MOV_{random.randint(100000, 999999)}",
                "inventory_id": inv["inventory_id"],
                "facility_id": inv["facility_id"],
                "batch_id": batch_id,
                "med_id": inv["med_id"],
                "movement_type": "DISPENSE",
                "quantity_change": -(excess_qty // 5),
                "quantity_after": 0,
                "timestamp": (
                    self.current_time + timedelta(minutes=i * 10)
                ).isoformat(),
                "reference_id": "ANOMALY_INJECT",
                "source": "SIMULATION_ANOMALY",
                "reason": "IMPOSSIBLE_QTY_TEST",
            }
            self.movements_log.append(mov)

        print(
            f"Injected: Batch {batch_id} dispensed {excess_qty} (initial was {initial_qty})"
        )


if __name__ == "__main__":

    meds = generate_medications()
    brands = generate_brands(meds)
    companies = generate_companies()
    batches = generate_batches(brands, companies)
    facilities = generate_facilities()
    inventory = generate_inventory(facilities, batches, meds, brands)

    # create and run simulation
    engine = SimulationEngine(
        inventory=inventory,
        medications=meds,
        facilities=facilities,
        batches=batches,
        start_time=START_TIME,
        end_time=END_TIME,
    )

    engine.initialize()
    result = engine.run()
