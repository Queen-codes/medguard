import random
from datetime import datetime, timedelta
from collections import defaultdict


def dispense(
    inventory,
    quantity,
    timestamp,
    source="UNKNOWN",
    reason="UNSPECIFIED",
):
    """
    for recording that medicine was dispensed from a batch simulating real-life dispense.
    """
    return _record_movement(
        inventory=inventory,
        movement_type="DISPENSE",
        quantity_change=-abs(quantity),
        timestamp=timestamp,
        reference_id=f"DIS_{random.randint(10000, 999999)}",
        source=source,
        reason=reason,
    )


def restock(inventory, quantity, timestamp, source="UNKNOWN"):
    """
    for recording the movement restock of a batch of med
    """
    return _record_movement(
        inventory=inventory,
        movement_type="RESTOCK",
        quantity_change=abs(quantity),
        timestamp=timestamp,
        reference_id=f"RES_{random.randint(10000, 999999)}",
        source=source,
    )


def transfer_out(
    inventory,
    quantity,
    timestamp,
    destination_facility_id,
    transfer_id=None,
    source="UNKNOWN",
):
    """
    for meds that leave a facility when a transfer request is fuffilled
    """
    mov = _record_movement(
        inventory=inventory,
        movement_type="TRANSFER_OUT",
        quantity_change=-abs(quantity),
        timestamp=timestamp,
        reference_id=f"TRF_TO_{destination_facility_id}",
        source=source,
    )
    # this records the transfer id for if/when a transfer request is inititated
    mov["transfer_id"] = transfer_id or f"TXF_{random.randint(10000, 99999)}"
    mov["destination_facility_id"] = destination_facility_id
    return mov


def transfer_in(
    inventory,
    quantity,
    timestamp,
    source_facility_id,
    transfer_id=None,
    source="UNKNOWN",
):
    """
    Record stock arriving at a facility.
    """
    mov = _record_movement(
        inventory=inventory,
        movement_type="TRANSFER_IN",
        quantity_change=abs(quantity),
        timestamp=timestamp,
        reference_id=f"TRF_FROM_{source_facility_id}",
        source=source,
    )
    mov["transfer_id"] = transfer_id or f"TXF_{random.randint(10000, 99999)}"
    mov["source_facility_id"] = source_facility_id
    return mov


def expiry_withdraw(inventory, quantity, timestamp, source="UNKNOWN"):
    """
    to track stock that was removed from shelf due to expiry
    """
    # to prevent withdrawing more than available since expiry might want to withdraw the whole quantity of expired batch
    # safe quantity lets it remove the actual quantity left.
    safe_quantity = min(abs(quantity), inventory["quantity"])
    return _record_movement(
        inventory=inventory,
        movement_type="EXPIRY_WITHDRAW",
        quantity_change=-safe_quantity,
        timestamp=timestamp,
        reference_id="EXPIRY_AUDIT",
        source=source,
    )


def _record_movement(
    inventory,
    movement_type,
    quantity_change,
    timestamp,
    reference_id,
    source="UNKNOWN",
    reason="UNSPECIFIED",
):
    """
    function that:
    - updates inventory quantity
    - returns a movement record
    """

    # check if timestamp is a datetime object.
    if isinstance(timestamp, datetime):
        timestamp = timestamp.isoformat()

    previous_quantity = inventory["quantity"]
    new_quantity = max(0, previous_quantity + quantity_change)

    movement = {
        "movement_id": f"MOV_{random.randint(100000, 999999)}",
        "inventory_id": inventory["inventory_id"],
        "facility_id": inventory["facility_id"],
        "batch_id": inventory["batch_id"],
        "med_id": inventory["med_id"],
        "movement_type": movement_type,
        "quantity_before": previous_quantity,
        "quantity_change": quantity_change,
        "quantity_after": new_quantity,
        "timestamp": timestamp,
        "reference_id": reference_id,
        "source": source,
        "reason": reason,
    }

    inventory["quantity"] = new_quantity
    return movement


def seed_historical_movements(inventory, medications, start_date, days=30, seed=42):

    random.seed(seed)
    movements = []

    med_lookup = {m["med_id"]: m for m in medications}
    inventory_by_med = defaultdict(list)

    for inv in inventory:
        inventory_by_med[inv["med_id"]].append(inv)

    for day in range(days):
        day_time = start_date + timedelta(days=day)

        for med_id, batches in inventory_by_med.items():
            daily_demand = med_lookup[med_id]["base_demand"] / 30

            for batch in batches:
                if batch["quantity"] <= 0:
                    continue

                if random.random() < 0.05:
                    qty = max(1, int(daily_demand * random.uniform(2.5, 4.0)))
                else:
                    qty = max(1, int(random.gauss(daily_demand, daily_demand * 0.35)))
                qty = min(qty, batch["quantity"])

                movements.append(
                    dispense(
                        batch,
                        qty,
                        day_time + timedelta(hours=12),
                        source="HISTORICAL_SEED",
                    )
                )

    return movements


if __name__ == "__main__":
    from medguard.data.generators.inventory import generate_inventory
    from medguard.data.generators.companies import generate_companies
    from medguard.data.generators.brands import generate_brands
    from medguard.data.generators.batches import generate_batches
    from medguard.data.generators.facilities import generate_facilities
    from medguard.data.generators.medications import generate_medications

    meds = generate_medications()
    brands = generate_brands(meds)
    companies = generate_companies()
    batches = generate_batches(brands, companies)
    facilities = generate_facilities()
    inventory = generate_inventory(facilities, batches, meds)

    start_date = datetime(2025, 11, 12)
    movement = seed_historical_movements(inventory, meds, start_date)
    # print(movement[0])

"""{
    "movement_id": "MOV_246316",
    "inventory_id": "INV_00001",
    "facility_id": "FAC_001",
    "batch_id": "BAT_0006",
    "med_id": "MED_001",
    "movement_type": "DISPENSE",
    "quantity_before": 242,
    "quantity_change": -8,
    "quantity_after": 234,
    "timestamp": "2025-11-12T12:00:00",
    "reference_id": "DIS_244053",
    "source": "HISTORICAL_SEED",
    "reason": "UNSPECIFIED",
}"""
