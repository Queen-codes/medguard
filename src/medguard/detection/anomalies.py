from datetime import datetime
from collections import defaultdict
from typing import List, Dict
import math
import uuid

from medguard.data.generators.companies import authorized_importers

ANOMALY_TYPES = [
    "IMPOSSIBLE_QUANTITY",
    "GEOGRAPHIC_IMPOSSIBILITY",
    "GHOST_STOCK",
    "UNAUTHORIZED_IMPORTER",
    "PRICE_ANOMALY",
    "DUPLICATE_BATCH_NUMBER",
]

DEFAULT_THRESHOLDS = {
    "IMPOSSIBLE_QUANTITY_MULTIPLIER": 10,
    "GEOGRAPHIC_IMPOSSIBLE_KM": 300,
    "GEOGRAPHIC_IMPOSSIBLE_HOURS": 6,
    "PRICE_ANOMALY_LOW_THRESHOLD": 0.7,
}


def create_anomaly(
    *,
    anomaly_type: str,
    severity: str,
    facility_id: str | None,
    med_id: str | None,
    timestamp: datetime,
    details: str,
    batch_id: str | None = None,
    evidence: Dict | None = None,
) -> Dict:
    return {
        "anomaly_id": f"ANOM_{uuid.uuid4().hex[:10].upper()}",
        "anomaly_type": anomaly_type,
        "severity": severity,
        "facility_id": facility_id,
        "med_id": med_id,
        "batch_id": batch_id,
        "timestamp": timestamp.isoformat(),
        "details": details,
        "evidence": evidence or {},
        "source": "SIMULATION",
        "is_active": True,
    }


# harversine function to calcuate distance between two locations
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# anomalies based on movements
def detect_impossible_quantity(
    movements: List[Dict],
    inventory: List[Dict],
    batches: List[Dict],
    current_time: datetime,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:
    anomalies = []

    initial_qty_by_batch = {b["batch_id"]: b["initial_quantity"] for b in batches}

    dispensed_by_batch = defaultdict(int)
    # get the amount dispensed already per batch
    for mov in movements:
        if mov["movement_type"] == "DISPENSE":
            dispensed_by_batch[mov["batch_id"]] += abs(mov["quantity_change"])

    for batch_id, dispensed in dispensed_by_batch.items():
        initial = initial_qty_by_batch.get(batch_id)
        if not initial:
            continue

        if dispensed > initial * thresholds["IMPOSSIBLE_QUANTITY_MULTIPLIER"]:
            anomalies.append(
                create_anomaly(
                    anomaly_type="IMPOSSIBLE_QUANTITY",
                    severity="CRITICAL",
                    facility_id=None,
                    med_id=None,
                    batch_id=batch_id,
                    timestamp=current_time,
                    details=f"Dispensed {dispensed} units but initial was {initial}",
                    evidence={
                        "initial_quantity": initial,
                        "dispensed_quantity": dispensed,
                        "ratio": round(dispensed / initial, 2),
                    },
                )
            )

    return anomalies


def detect_geographic_impossibility(
    movements: List[Dict],
    facilities: List[Dict],
    current_time: datetime,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:
    """detect when same batch appears at distant locations in an unrealistic short period."""
    anomalies = []

    facility_lookup = {f["facility_id"]: f for f in facilities}
    movements_by_batch = defaultdict(list)

    for mov in movements:
        # skip initial seed
        if mov.get("source") == "INITIAL_SEED":
            continue
        #  check restock  movements only
        if mov["movement_type"] != "RESTOCK":
            continue
        movements_by_batch[mov["batch_id"]].append(mov)

    for batch_id, batch_moves in movements_by_batch.items():
        # sort batch movements with time
        batch_moves.sort(key=lambda movement: movement["timestamp"])

        for i in range(len(batch_moves) - 1):
            former_movement = batch_moves[i]
            latter_movement = batch_moves[i + 1]

            former_fac = facility_lookup.get(former_movement["facility_id"])
            latter_fac = facility_lookup.get(latter_movement["facility_id"])

            if not former_fac or not latter_fac:
                continue

            # skip same facility
            if former_fac["facility_id"] == latter_fac["facility_id"]:
                continue

            former_time = datetime.fromisoformat(former_movement["timestamp"])
            latter_time = datetime.fromisoformat(latter_movement["timestamp"])
            hours_between = abs((latter_time - former_time).total_seconds()) / 3600

            distance_in_km = haversine_km(
                former_fac["latitude"],
                former_fac["longitude"],
                latter_fac["latitude"],
                latter_fac["longitude"],
            )

            if (
                distance_in_km > thresholds["GEOGRAPHIC_IMPOSSIBLE_KM"]
                and hours_between < thresholds["GEOGRAPHIC_IMPOSSIBLE_HOURS"]
            ):
                anomalies.append(
                    create_anomaly(
                        anomaly_type="GEOGRAPHIC_IMPOSSIBILITY",
                        severity="CRITICAL",
                        facility_id=None,
                        med_id=former_movement["med_id"],
                        batch_id=batch_id,
                        timestamp=current_time,
                        details=f"Batch appeared at two distant locations ({round(distance_in_km, 1)} km apart) within {round(hours_between, 2)} hours",
                        evidence={
                            "first_facility": former_fac["facility_id"],
                            "second_facility": latter_fac["facility_id"],
                            "distance_km": round(distance_in_km, 1),
                            "hours_between": round(hours_between, 2),
                        },
                    )
                )

    return anomalies


def detect_ghost_stock(
    inventory: List[Dict],
    movements: List[Dict],
    current_time: datetime,
) -> List[Dict]:
    """Detect inventory that exists without any movement at that facility."""
    anomalies = []

    received_at_facility = set()
    for mov in movements:
        if mov["movement_type"] in ("RESTOCK", "TRANSFER_IN"):
            key = (mov["facility_id"], mov["batch_id"])
            received_at_facility.add(key)

    for inv in inventory:
        if inv["quantity"] <= 0:
            continue

        key = (inv["facility_id"], inv["batch_id"])
        if key not in received_at_facility:
            anomalies.append(
                create_anomaly(
                    anomaly_type="GHOST_STOCK",
                    severity="HIGH",
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details="Inventory exists at facility without any receipt movement",
                    evidence={
                        "quantity": inv["quantity"],
                        "facility_id": inv["facility_id"],
                    },
                )
            )

    return anomalies


def detect_unauthorized_importer(
    batches: List[Dict],
    current_time: datetime,
) -> List[Dict]:
    """Detect batches imported by unauthorized importers."""
    anomalies = []

    for batch in batches:
        manufacturer_name = batch.get("manufacturer_name")
        importer_name = batch.get("importer_name")

        # skip nigerian manufacturers because they can self-distribute
        if manufacturer_name == importer_name:
            continue

        # does manufacturer have authorized importers ?
        authorized = authorized_importers.get(manufacturer_name)

        # not an international manufacturer requiring authorization, skip
        if authorized is None:
            continue

        if importer_name not in authorized:
            anomalies.append(
                create_anomaly(
                    anomaly_type="UNAUTHORIZED_IMPORTER",
                    severity="CRITICAL",
                    facility_id=None,
                    med_id=batch["med_id"],
                    batch_id=batch["batch_id"],
                    timestamp=current_time,
                    details=f"Batch imported by unauthorized importer: {importer_name}",
                    evidence={
                        "manufacturer": manufacturer_name,
                        "importer": importer_name,
                        "authorized_importers": authorized,
                    },
                )
            )

    return anomalies


def detect_duplicate_batch_number(
    batches: List[Dict],
    current_time: datetime,
) -> List[Dict]:
    """detect batches with duplicate batch numbers."""
    anomalies = []

    # group batches by batch no
    by_batch_number = defaultdict(list)
    for batch in batches:
        by_batch_number[batch["batch_number"]].append(batch)

    for batch_number, batch_list in by_batch_number.items():
        if len(batch_list) > 1:
            batch_ids = [b["batch_id"] for b in batch_list]
            manufacturers = list(set(b["manufacturer_name"] for b in batch_list))

            anomalies.append(
                create_anomaly(
                    anomaly_type="DUPLICATE_BATCH_NUMBER",
                    severity="CRITICAL",
                    facility_id=None,
                    med_id=batch_list[0]["med_id"],
                    batch_id=batch_ids[0],
                    timestamp=current_time,
                    details=f"Batch number {batch_number} appears on {len(batch_list)} different batches",
                    evidence={
                        "batch_number": batch_number,
                        "duplicate_batch_ids": batch_ids,
                        "manufacturers": manufacturers,
                    },
                )
            )

    return anomalies


def detect_price_anomaly(
    inventory: List[Dict],
    current_time: datetime,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:

    anomalies = []

    for inv in inventory:
        actual_price = inv.get("unit_price")
        expected_price = inv.get("expected_price")

        if not actual_price or not expected_price or expected_price <= 0:
            continue

        ratio = actual_price / expected_price

        if ratio < thresholds["PRICE_ANOMALY_LOW_THRESHOLD"]:
            anomalies.append(
                create_anomaly(
                    anomaly_type="PRICE_ANOMALY",
                    severity="HIGH",
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details=f"Suspiciously low price: {actual_price} vs expected {expected_price}",
                    evidence={
                        "actual_price": actual_price,
                        "expected_price": expected_price,
                        "price_ratio": round(ratio, 2),
                        "counterfeit_risk": inv.get("counterfeit_risk"),
                        "facility_id": inv["facility_id"],
                    },
                )
            )

    return anomalies


def generate_anomalies(
    *,
    inventory: List[Dict],
    movements: List[Dict],
    events: List[Dict],
    facilities: List[Dict],
    batches: List[Dict],
    current_time: datetime,
    existing_anomalies: List[Dict] = None,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:

    existing_anomalies = existing_anomalies or []

    # Create signatures of already-detected anomalies
    existing_signatures = set()
    for a in existing_anomalies:
        sig = (
            a["anomaly_type"],
            a.get("facility_id"),
            a.get("batch_id"),
            a.get("med_id"),
        )
        existing_signatures.add(sig)

    all_detected = []
    all_detected.extend(
        detect_impossible_quantity(
            movements, inventory, batches, current_time, thresholds
        )
    )
    all_detected.extend(
        detect_geographic_impossibility(movements, facilities, current_time, thresholds)
    )
    all_detected.extend(detect_ghost_stock(inventory, movements, current_time))
    all_detected.extend(detect_unauthorized_importer(batches, current_time))
    all_detected.extend(detect_duplicate_batch_number(batches, current_time))
    all_detected.extend(detect_price_anomaly(inventory, current_time, thresholds))

    # fulter duplicates
    new_anomalies = []
    for anomaly in all_detected:
        sig = (
            anomaly["anomaly_type"],
            anomaly.get("facility_id"),
            anomaly.get("batch_id"),
            anomaly.get("med_id"),
        )
        if sig not in existing_signatures:
            new_anomalies.append(anomaly)
            existing_signatures.add(sig)

    return new_anomalies


if __name__ == "__main__":
    from medguard.data.generators.medications import generate_medications
    from medguard.data.generators.brands import generate_brands
    from medguard.data.generators.companies import generate_companies
    from medguard.data.generators.batches import generate_batches
    from medguard.data.generators.facilities import generate_facilities
    from medguard.data.generators.inventory import generate_inventory

    meds = generate_medications()
    brands = generate_brands(meds)
    companies = generate_companies()
    batches = generate_batches(brands, companies)
    facilities = generate_facilities()
    inventory = generate_inventory(facilities, batches, meds, brands)

    current_time = datetime(2026, 1, 3, 10, 0)
    movements = []  # empty to show ghost stock

    all_anomalies = generate_anomalies(
        inventory=inventory,
        movements=movements,
        events=[],
        facilities=facilities,
        batches=batches,
        current_time=current_time,
    )
    # print(f"Total: {len(all_anomalies)}")
