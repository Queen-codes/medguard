from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict
import uuid

SEVERITY_LEVELS = {
    "INFO": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

EVENT_TYPES = [
    "LOW_STOCK",
    "STOCKOUT",
    "NEAR_EXPIRY",
    "EXPIRED_IN_STOCK",
    "RAPID_CONSUMPTION",
]

DEFAULT_THRESHOLDS = {
    "NEAR_EXPIRY_DAYS": 30,
    "URGENT_EXPIRY_DAYS": 14,
    "RAPID_CONSUMPTION_WINDOW_HOURS": 24,
    "RAPID_CONSUMPTION_MULTIPLIER": 2.0,
}


def create_event(
    *,
    event_type: str,
    severity: str,
    facility_id: str,
    med_id: str,
    timestamp: datetime,
    details: str,
    batch_id: str | None = None,
    data: Dict | None = None,
) -> Dict:
    """
    creates the structure all events should follow and uses * to ensure keyword paramaters usage only
    """
    return {
        "event_id": f"EVT_{uuid.uuid4().hex[:10].upper()}",
        "event_type": event_type,
        "severity": severity,
        "facility_id": facility_id,
        "med_id": med_id,
        "batch_id": batch_id,
        "timestamp": timestamp.isoformat(),  # when event occured
        "detected_at": datetime.now().isoformat(),  # when the agent wakes up and detects the event
        "details": details,
        "data": data or {},
        "source": "SIMULATION",
        "is_active": True,
    }


# events
def detect_low_stock(inventory: List[Dict], current_time: datetime) -> List[Dict]:
    events = []

    for inv in inventory:
        quantity = inv["quantity"]
        reorder_point = inv["reorder_point"]

        if 0 < quantity <= reorder_point:
            events.append(
                create_event(
                    event_type="LOW_STOCK",
                    severity="MEDIUM",
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details=(
                        f"Stock is low: quantity={quantity}, "
                        f"reorder_point={reorder_point}"
                    ),
                    data={
                        "quantity": quantity,
                        "reorder_point": reorder_point,
                    },
                )
            )

    return events


def detect_stockout(inventory: List[Dict], current_time: datetime) -> List[Dict]:
    events = []

    for inv in inventory:
        if inv["quantity"] == 0:
            events.append(
                create_event(
                    event_type="STOCKOUT",
                    severity="CRITICAL",
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details="Stockout detected: quantity is zero",
                )
            )

    return events


def detect_near_expiry(
    inventory: List[Dict],
    current_time: datetime,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:
    events = []

    for inv in inventory:
        if inv["quantity"] <= 0:
            continue

        try:
            expiry_date = datetime.strptime(inv["expiry_date"], "%Y-%m-%d")
        except ValueError:
            continue

        days_to_expiry = (expiry_date - current_time).days

        if 0 < days_to_expiry <= thresholds["NEAR_EXPIRY_DAYS"]:
            severity = (
                "HIGH"
                if days_to_expiry <= thresholds["URGENT_EXPIRY_DAYS"]
                else "MEDIUM"
            )

            events.append(
                create_event(
                    event_type="NEAR_EXPIRY",
                    severity=severity,
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details=f"Batch expires in {days_to_expiry} days",
                    data={"days_to_expiry": days_to_expiry},
                )
            )

    return events


def detect_expired_in_stock(
    inventory: List[Dict],
    current_time: datetime,
) -> List[Dict]:
    events = []

    for inv in inventory:
        if inv["quantity"] <= 0:
            continue

        try:
            expiry_date = datetime.strptime(inv["expiry_date"], "%Y-%m-%d")
        except ValueError:
            continue

        if current_time >= expiry_date:
            events.append(
                create_event(
                    event_type="EXPIRED_IN_STOCK",
                    severity="HIGH",
                    facility_id=inv["facility_id"],
                    med_id=inv["med_id"],
                    batch_id=inv["batch_id"],
                    timestamp=current_time,
                    details="Expired stock still present in inventory",
                )
            )

    return events


def detect_rapid_consumption(
    movements: List[Dict],
    inventory: List[Dict],
    medications: List[Dict],
    current_time: datetime,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:
    events = []

    window_start = current_time - timedelta(
        hours=thresholds["RAPID_CONSUMPTION_WINDOW_HOURS"]
    )

    dispensed = defaultdict(int)

    for m in movements:
        if m["movement_type"] != "DISPENSE":
            continue

        ts = datetime.fromisoformat(m["timestamp"])
        if ts < window_start:
            continue

        key = (m["facility_id"], m["med_id"])
        dispensed[key] += abs(m["quantity_change"])

    # Expected demand
    """base_demand_by_med = {}
    for inv in inventory:
        base_demand_by_med.setdefault(inv["med_id"], inv.get("base_demand"))"""

    med_lookup = {m["med_id"]: m["base_demand"] for m in medications}

    for (facility_id, med_id), qty in dispensed.items():
        expected = med_lookup.get(med_id)
        if not expected:
            continue

        if qty > expected * thresholds["RAPID_CONSUMPTION_MULTIPLIER"]:
            events.append(
                create_event(
                    event_type="RAPID_CONSUMPTION",
                    severity="MEDIUM",
                    facility_id=facility_id,
                    med_id=med_id,
                    batch_id=None,
                    timestamp=current_time,
                    details=(
                        f"Dispensed {qty} units in "
                        f"{thresholds['RAPID_CONSUMPTION_WINDOW_HOURS']}h "
                        f"(expected ~{expected})"
                    ),
                    data={
                        "dispensed_quantity": qty,
                        "expected_quantity": expected,
                    },
                )
            )

    return events


# event generator
def generate_events(
    *,
    inventory: List[Dict],
    movements: List[Dict],
    medications: List[Dict],
    current_time: datetime,
    existing_events: List[Dict] = None,
    thresholds=DEFAULT_THRESHOLDS,
) -> List[Dict]:

    existing_events = existing_events or []

    # create signatures of active events
    existing_signatures = set()
    for e in existing_events:
        if e.get("is_active", True):
            sig = (e["event_type"], e["facility_id"], e["med_id"], e.get("batch_id"))
            existing_signatures.add(sig)

    # detect all events
    all_detected = []
    all_detected.extend(detect_low_stock(inventory, current_time))
    all_detected.extend(detect_stockout(inventory, current_time))
    all_detected.extend(detect_near_expiry(inventory, current_time, thresholds))
    all_detected.extend(detect_expired_in_stock(inventory, current_time))
    all_detected.extend(
        detect_rapid_consumption(
            movements, inventory, medications, current_time, thresholds
        )
    )

    # filter duplicates
    new_events = []
    for event in all_detected:
        sig = (
            event["event_type"],
            event["facility_id"],
            event["med_id"],
            event.get("batch_id"),
        )
        if sig not in existing_signatures:
            new_events.append(event)
            existing_signatures.add(sig)

    return new_events
