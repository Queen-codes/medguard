from datetime import datetime, timedelta
import random

from generators.companies import authorized_importers


def generate_batches(brands, companies, batches_per_brand=(2, 5), seed=42):
    """
    Generate a batch record for each brand.

    Args:
        brands: List of brands from generate_brands
        companies: List of comp from generate_companies
        batches_per_brand: Tuple (min, max) batches to generate per brand

    Returns:
        List of batch dictionary
    """
    random.seed(seed)

    # Create a dictionary to look up companies by their name, to find manufacturer deets by name
    company_lookup = {company["name"]: company for company in companies}
    # print(company_lookup)

    # Create a list of Nigerian importers by filtering companies that are in Nigeria and marked as importers
    nigerian_importers = []
    for company in companies:
        if company["country"] == "Nigeria" and company["is_importer"]:
            nigerian_importers.append(company)

    batches = []
    batch_counter = 1

    # Set a fixed reference date
    today = datetime(2025, 1, 15)

    # Loop through each brand in the brands list
    for brand in brands:
        # Get the manufacturer name from the brand
        manufacturer_name = brand["manufacturer"]
        # print(manufacturer_name)  # Emzor Pharmaceutical

        # getthe manufacturer company using the company_lookup
        manufacturer = company_lookup.get(manufacturer_name)
        # print(manufacturer)  # returns a company dict

        if not manufacturer:
            print(f"Manufacturer {manufacturer_name} not in companies ")
            continue

        # Based on brand's counterfeit_risk, how many batches for thus brand?
        if brand["counterfeit_risk"] == "HIGH":
            num_batches = random.randint(3, batches_per_brand[1])
        elif brand["counterfeit_risk"] == "MEDIUM":
            num_batches = random.randint(2, 4)
        else:
            num_batches = random.randint(batches_per_brand[0], 3)

        # Loop num_batches times to generate each batch for this brand
        for _ in range(num_batches):
            # randomly fix the manufacturing and expirty date
            days_ago = random.randint(30, 540)
            manufacturing_date = today - timedelta(days=days_ago)
            shelf_life_days = random.randint(730, 1095)
            expiry_date = manufacturing_date + timedelta(days=shelf_life_days)

            # Initial quantity produced more for more freq brands
            if brand["counterfeit_risk"] == "HIGH":
                initial_quantity = random.randint(5000, 20000)
            else:
                initial_quantity = random.randint(2000, 10000)

            # importer
            if manufacturer["country"] == "Nigeria":
                importer_id = manufacturer["company_id"]
                # importer_name = manufacturer["name"]
                importer_name = manufacturer_name
            else:
                authorized = authorized_importers.get(manufacturer_name, [])

                # 5% chance of unauthorized importer (for anomaly detection)
                if random.random() < 0.05 or not authorized:
                    fallback = random.choice(nigerian_importers)
                    importer_name = fallback["name"]
                    importer_id = fallback["company_id"]
                else:
                    importer_name = random.choice(authorized)
                    importer = company_lookup.get(importer_name)
                    importer_id = importer["company_id"]

            # batch number format
            # batch number which allows for rare duplicate
            if random.random() < 0.02 and batches:
                # reuse an existing batch number for anomaly
                batch_number = random.choice(batches)["batch_number"]
            else:
                code = manufacturer_name[:3].upper()
                year = manufacturing_date.year
                batch_number = f"{code}-{year}-{batch_counter:04d}"

            # price anomaly
            price_multiplier = random.uniform(0.6, 1.1)
            unit_price = int(brand["unit_price"] * price_multiplier)

            batch = {
                "batch_id": f"BAT_{batch_counter:04d}",
                "brand_id": brand["brand_id"],
                "brand_name": brand["brand_name"],
                "med_id": brand["med_id"],
                "generic_name": brand["generic_name"],
                "manufacturer_id": manufacturer["company_id"],
                "manufacturer_name": manufacturer_name,
                "importer_id": importer_id,
                "importer_name": importer_name,
                "batch_number": batch_number,
                "manufacturing_date": manufacturing_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "initial_quantity": initial_quantity,
                "unit_price": unit_price,
                "counterfeit_risk": brand["counterfeit_risk"],
                "is_verified": True,
                "is_flagged": False,
            }
            batches.append(batch)
            batch_counter += 1
    return batches


if __name__ == "__main__":
    from generators.brands import generate_brands
    from generators.companies import generate_companies
    from generators.medications import generate_medications

    meds = generate_medications()
    companies = generate_companies()
    brands = generate_brands(meds)
    batches = generate_batches(brands, companies)

    # print(f"Generated {len(batches)} batches for {len(brands)} brands")
    # print(f"{batches[0]}")

# Generated 212 batches for 70 brands
"""
{
    "batch_id": "BAT_0001",
    "brand_id": "BRD_001",
    "brand_name": "Coartem",
    "med_id": "MED_001",
    "generic_name": "Artemether-Lumefantrine",
    "manufacturer_id": "COMP_001",
    "manufacturer_name": "Novartis",
    "importer_id": "COMP_018",
    "importer_name": "WWCVL",
    "batch_number": "NOV-2024-0001",
    "manufacturing_date": "2024-10-20",
    "expiry_date": "2026-11-01",
    "initial_quantity": 17149,
    "unit_price": 2279,
    "counterfeit_risk": "HIGH",
    "is_verified": True,
    "is_flagged": False,
}
"""
