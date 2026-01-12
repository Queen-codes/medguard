from medguard.db.database import (
    init_database,
    clear_database,
    get_connection_to_db,
    insert_medications,
    insert_companies,
    insert_facilities,
    insert_brands,
    insert_batches,
    insert_inventory,
)

from medguard.data.generators.medications import generate_medications
from medguard.data.generators.companies import generate_companies
from medguard.data.generators.facilities import generate_facilities
from medguard.data.generators.brands import generate_brands
from medguard.data.generators.batches import generate_batches
from medguard.data.generators.inventory import generate_inventory


def seed_database():
    init_database()
    clear_database()

    medications = generate_medications()
    companies = generate_companies()
    facilities = generate_facilities()
    brands = generate_brands(medications)
    batches = generate_batches(brands, companies)
    inventory = generate_inventory(facilities, batches, medications, brands)

    conn = get_connection_to_db()

    insert_medications(medications, conn)
    insert_companies(companies, conn)
    insert_facilities(facilities, conn)
    insert_brands(brands, conn)
    insert_batches(batches, conn)
    insert_inventory(inventory, conn)

    conn.commit()
    conn.close()
    print("Database seeded successfully")


if __name__ == "__main__":
    seed_database()
