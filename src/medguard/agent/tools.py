from medguard.db.database import get_connection_to_db
from medguard.agent.registry import registry


@registry.register
def query_inventory(facility_id: str, medication_id: str) -> dict:
    """
    Get current inventory level for a specific medication at a specific facility.
    Use this to check stock quantities.
    """
    conn = get_connection_to_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SUM(inventory.quantity) AS total_quantity
        FROM inventory
        JOIN batches ON inventory.batch_id = batches.batch_id
        JOIN brands ON batches.brand_id = brands.brand_id
        WHERE inventory.facility_id = ?
          AND brands.med_id = ?
        """,
        (facility_id, medication_id),
    )

    row = cursor.fetchone()
    conn.close()

    return {
        "facility_id": facility_id,
        "medication_id": medication_id,
        "quantity": row["total_quantity"] or 0 if row else 0,
    }
