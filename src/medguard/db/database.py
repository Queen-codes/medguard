import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

# path_to_db = Path(__file__).parent / "medguard.db"
# path_to_schema = Path(__file__).parent / "schema.sql"

BASE_DIR = Path(__file__).resolve().parent

path_to_db = BASE_DIR / "medguard.db"
path_to_schema = BASE_DIR / "schema.sql"

# conn = sqlite3.connect(path_to_db)
# conn.execute("PRAGMA foreign_keys = ON")
# conn.row_factory = sqlite3.Row
# cur = conn.cursor()


def get_connection_to_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or path_to_db
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Optional[Path] = None) -> None:
    conn = get_connection_to_db(db_path)
    with open(path_to_schema) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def clear_database(db_path: Optional[Path] = None) -> None:
    """Clear all data (keeps schema)."""
    conn = get_connection_to_db(db_path)
    # list tables in order of no dependency to dependency order
    tables = [
        "anomalies",
        "events",
        "movements",
        "inventory",
        "batches",
        "brands",
        "facilities",
        "companies",
        "medications",
    ]
    for table in tables:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()


def insert_medications(medications: List[Dict], conn: sqlite3.Connection) -> None:
    if not medications:
        return

    sql = """
        INSERT OR REPLACE INTO medications (
            med_id,
            generic_name,
            therapeutic_class,
            form,
            strength,
            category,
            base_demand,
            stocking_level,
            is_cold_chain,
            nrn
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            med["med_id"],
            med["generic_name"],
            med.get("therapeutic_class"),
            med.get("form"),
            med.get("strength"),
            med.get("category"),
            med.get("base_demand"),
            med.get("stocking_level"),
            int(bool(med.get("is_cold_chain", False))),
            med.get("nrn"),
        )
        for med in medications
    ]

    with conn:
        conn.executemany(sql, values)


def insert_companies(companies: List[Dict], conn: sqlite3.Connection) -> None:
    if not companies:
        return

    sql = """
        INSERT OR REPLACE INTO companies (
            company_id,
            name,
            country,
            city,
            is_manufacturer,
            is_importer,
            is_distributor
        )
        VALUES(?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            company["company_id"],
            company["name"],
            company.get("country"),
            company.get("city"),
            int(bool(company.get("is_manufacturer", False))),
            int(bool(company.get("is_importer", False))),
            int(bool(company.get("is_distributor", False))),
        )
        for company in companies
    ]
    with conn:
        conn.executemany(sql, values)


def insert_facilities(facilities: List[Dict], conn: sqlite3.Connection) -> None:
    if not facilities:
        return

    sql = """
        INSERT OR REPLACE INTO facilities (
            facility_id,
            name,
            facility_type,
            city,
            state,
            tier,
            has_cold_storage,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            facility["facility_id"],
            facility["name"],
            facility.get("facility_type"),
            facility.get("city"),
            facility.get("state"),
            facility.get("tier"),
            int(bool(facility.get("has_cold_storage", False))),
            facility.get("latitude"),
            facility.get("longitude"),
        )
        for facility in facilities
    ]

    with conn:
        conn.executemany(sql, values)


def insert_brands(brands: List[Dict], conn: sqlite3.Connection) -> None:
    if not brands:
        return

    sql = """
        INSERT OR REPLACE INTO brands (
            brand_id,
            brand_name,
            med_id,
            manufacturer_id,
            unit_price,
            is_innovator,
            counterfeit_risk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            brand["brand_id"],
            brand["brand_name"],
            brand["med_id"],
            brand.get("manufacturer_id"),
            brand.get("unit_price"),
            int(bool(brand.get("is_innovator", False))),
            brand.get("counterfeit_risk"),
        )
        for brand in brands
    ]

    with conn:
        conn.executemany(sql, values)


def insert_batches(batches: List[Dict], conn: sqlite3.Connection) -> None:
    if not batches:
        return

    sql = """
        INSERT OR REPLACE INTO batches (
            batch_id,
            brand_id,
            importer_id,
            batch_number,
            manufacturing_date,
            expiry_date,
            initial_quantity,
            is_verified,
            is_flagged
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            batch["batch_id"],
            batch["brand_id"],
            batch.get("importer_id"),
            batch.get("batch_number"),
            batch.get("manufacturing_date"),
            batch.get("expiry_date"),
            batch.get("initial_quantity"),
            int(bool(batch.get("is_verified", True))),
            int(bool(batch.get("is_flagged", False))),
        )
        for batch in batches
    ]

    with conn:
        conn.executemany(sql, values)


def insert_inventory(inventory: List[Dict], conn: sqlite3.Connection) -> None:
    if not inventory:
        return

    sql = """
        INSERT OR REPLACE INTO inventory (
            inventory_id,
            facility_id,
            batch_id,
            quantity,
            reorder_point,
            unit_price
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            item["inventory_id"],
            item["facility_id"],
            item["batch_id"],
            item["quantity"],
            item.get("reorder_point"),
            item.get("unit_price"),
        )
        for item in inventory
    ]

    with conn:
        conn.executemany(sql, values)


def insert_movements(movements: List[Dict], conn: sqlite3.Connection) -> None:
    if not movements:
        return

    sql = """
        INSERT OR REPLACE INTO movements (
            movement_id,
            facility_id,
            batch_id,
            inventory_id,
            movement_type,
            quantity_before,
            quantity_change,
            quantity_after,
            timestamp,
            reference_id,
            source,
            reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            movement["movement_id"],
            movement["facility_id"],
            movement["batch_id"],
            movement.get("inventory_id"),
            movement["movement_type"],
            movement.get("quantity_before"),
            movement["quantity_change"],
            movement.get("quantity_after"),
            movement["timestamp"],
            movement.get("reference_id"),
            movement.get("source"),
            movement.get("reason"),
        )
        for movement in movements
    ]

    with conn:
        conn.executemany(sql, values)


def insert_events(events: List[Dict], conn: sqlite3.Connection) -> None:
    if not events:
        return

    sql = """
        INSERT OR REPLACE INTO events (
            event_id,
            event_type,
            severity,
            facility_id,
            batch_id,
            timestamp,
            detected_at,
            details,
            data,
            source,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            event["event_id"],
            event["event_type"],
            event.get("severity"),
            event.get("facility_id"),
            event.get("batch_id"),
            event.get("timestamp"),
            event.get("detected_at"),
            event.get("details"),
            event.get("data"),
            event.get("source"),
            int(bool(event.get("is_active", True))),
        )
        for event in events
    ]

    with conn:
        conn.executemany(sql, values)


def insert_anomalies(anomalies: List[Dict], conn: sqlite3.Connection) -> None:
    if not anomalies:
        return

    sql = """
        INSERT OR REPLACE INTO anomalies (
            anomaly_id,
            anomaly_type,
            severity,
            facility_id,
            batch_id,
            timestamp,
            details,
            evidence,
            source,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = [
        (
            anomaly["anomaly_id"],
            anomaly["anomaly_type"],
            anomaly.get("severity"),
            anomaly.get("facility_id"),
            anomaly.get("batch_id"),
            anomaly.get("timestamp"),
            anomaly.get("details"),
            anomaly.get("evidence"),
            anomaly.get("source"),
            int(bool(anomaly.get("is_active", True))),
        )
        for anomaly in anomalies
    ]

    with conn:
        conn.executemany(sql, values)


def get_snapshot_details(snapshot_id: str, conn) -> Dict:
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM agent_snapshots WHERE snapshot_id = ?", (snapshot_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"Snapshot not found: {snapshot_id}")

    snapshot = dict(row)

    # critical anomalies
    critical_ids = json.loads(snapshot["critical_anomaly_ids"] or "[]")

    if critical_ids:
        placeholders = ",".join(["?"] * len(critical_ids))
        cursor.execute(
            f"SELECT * FROM anomalies WHERE anomaly_id IN ({placeholders})",
            critical_ids,
        )
        snapshot["critical_anomalies"] = [dict(r) for r in cursor.fetchall()]
    else:
        snapshot["critical_anomalies"] = []

    return snapshot
