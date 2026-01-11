import random
from generators.medications_data import stocking_rule

seed = 42
random.seed(42)

# Multipliers for reorder point calculation based on facility tier
# reorder_point = base_demand * tier_multiplier * days_buffer
tier_multipliers = {
    "MAJOR": 1.5,  # High traffic, need more stock
    "SECONDARY": 1.0,  # Normal
    "TERTIARY": 0.6,
}

# Days of buffer stock to maintain (affects reorder point)
buffer_days = {
    "TEACHING_HOSPITAL": 14,
    "GENERAL_HOSPITAL": 10,
    "COMMUNITY_PHARMACY": 7,
    "PRIMARY_HEALTH_CENTER": 5,
}

# How much stock relative to reorder point (current stock / reorder_point ratio)
# below 1.0 - low stock
# above 1.0 - enough stock
# 1.0 - reorder point

stock_level_range = {
    "TEACHING_HOSPITAL": (1.5, 4.0),  # well_stocked
    "GENERAL_HOSPITAL": (1.0, 3.0),
    "COMMUNITY_PHARMACY": (0.8, 2.5),
    "PRIMARY_HEALTH_CENTER": (0.5, 2.0),
}


def calculate_reorder_point(base_demand, facility_type, tier):
    # Calculate reorder point( base_demand * tier_multiplier * (buffer_days / 30)) for a medication at a facility.
    tier_level = tier_multipliers.get(tier, 1.0)
    buffer = buffer_days.get(facility_type, 7)
    reorder_point = base_demand * tier_level * (buffer / 30)

    return max(10, int(reorder_point))  # reorder never below 10


def generate_inventory(facilities, batches, medications, brands):
    """
    Generate inventory records for all facilities.
    the inventory record should follow this rules:
    1. Stocking level - PHC can only stock level 1
    2. only store cold chain medications in facilites that have cold chain storage

    Args:
        facilities: List of facility dicts
        batches: List of batch dicts
        medications: List of medication dicts
        brands: List of brand dicts

    Returns:
        List of inventory dicts
    """

    # Group batches by medication
    batches_by_med = {}
    for batch in batches:
        med_id = batch["med_id"]

        if med_id not in batches_by_med:
            batches_by_med[med_id] = []
        batches_by_med[med_id].append(batch)
    # print(batches_by_med)

    # Brand lookup for price
    brand_lookup = {b["brand_id"]: b for b in brands}

    inventory = []
    inv_counter = 1

    for facility in facilities:
        fac_id = facility["facility_id"]
        fac_type = facility["facility_type"]
        fac_tier = facility["tier"]
        has_cold_storage = facility["has_cold_storage"]
        allowed_levels = stocking_rule.get(fac_type, [])

        for med in medications:
            med_id = med["med_id"]
            nafdac_number = med["nrn"]
            is_cold_chain = med["is_cold_chain"]
            base_demand = med["base_demand"]
            stocking_level = med["stocking_level"]

            # check stocking level
            if stocking_level not in allowed_levels:
                continue
            if is_cold_chain and not has_cold_storage:
                continue

            # Get available batches for this medication
            available_batches = batches_by_med.get(med_id, [])
            if not available_batches:
                continue

            reorder_point = calculate_reorder_point(base_demand, fac_type, fac_tier)

            # total stock level
            # stock_range = stock_level_range.get()
            stock_range = stock_level_range.get(fac_type, (1.0, 2.0))
            stock_multiplier = random.uniform(stock_range[0], stock_range[1])
            target_total = int(reorder_point * stock_multiplier)

            # different batches btw (1-3)
            num_batches = random.randint(1, min(3, len(available_batches)))
            selected_batches = random.sample(available_batches, num_batches)
            remaining = target_total

            for i, batch in enumerate(selected_batches):
                if i == len(selected_batches) - 1:
                    qty = remaining
                else:
                    qty = random.randint(remaining // 3, remaining // 2)
                    remaining -= qty

                #  If less tha 0, skip
                if qty <= 0:
                    continue

                # get price of brand
                brand = brand_lookup.get(batch["brand_id"])
                if not brand:
                    continue

                # 2% chance of suspicious low price as a counterfeit indicator
                if random.random() < 0.01:
                    price_multiplier = random.uniform(0.4, 0.6)  # low
                else:
                    price_multiplier = random.uniform(0.9, 1.1)  # Normal

                unit_price = int(brand["unit_price"] * price_multiplier)

                inv_record = {
                    "inventory_id": f"INV_{inv_counter:05d}",
                    "facility_id": fac_id,
                    "batch_id": batch["batch_id"],
                    "brand_id": batch["brand_id"],
                    "med_id": med_id,
                    "generic_name": med["generic_name"],
                    "brand_name": batch["brand_name"],
                    "facility_name": facility["name"],
                    "quantity": qty,
                    "reorder_point": reorder_point,
                    "expiry_date": batch["expiry_date"],
                    "unit_price": unit_price,
                    "expected_price": brand["unit_price"],  # for anomaly detection
                    "counterfeit_risk": batch.get("counterfeit_risk", "LOW"),
                }
                inventory.append(inv_record)
                inv_counter += 1

    return inventory


if __name__ == "__main__":
    from generators.batches import generate_batches
    from generators.brands import generate_brands
    from generators.companies import generate_companies
    from generators.facilities import generate_facilities
    from generators.medications import generate_medications

    meds = generate_medications()
    brands = generate_brands(meds)
    companies = generate_companies()
    batches = generate_batches(brands, companies)
    facilities = generate_facilities()

    inventory = generate_inventory(facilities, batches, meds, brands)
    print(f"Generated {len(inventory)} inv records")
    # print(f"{inventory[0]}")

    # Generated 2478 records

    """
    {
    'inventory_id': 'INV_00001', 
    'facility_id': 'FAC_001', 
    'batch_id': 'BAT_0008', 
    'brand_id': 'BRD_003', 
    'med_id': 'MED_001', 
    'generic_name': 'Artemether-Lumefantrine', 
    'brand_name': 'Combisunate', 
    'facility_name': 'Lagos University Teaching Hospital', 
    'quantity': 270, 
    'reorder_point': 93, 
    'expiry_date': '2026-07-10', 
    'unit_price': 1600
    }
    """
