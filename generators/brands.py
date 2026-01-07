from generators.brands_data import brands_data


def generate_brands(medications):

    med_lookup = {med["generic_name"]: med["med_id"] for med in medications}

    brands = []
    brand_counter = 1

    for generic_name, brand_list in brands_data.items():
        med_id = med_lookup.get(generic_name)

        if not med_id:
            print(f"No medication found for '{generic_name}'")
            continue

        for (
            brand_name,
            manufacturer,
            country,
            price,
            is_innovator,
            counterfeit_risk,
        ) in brand_list:
            brand = {
                "brand_id": f"BRD_{brand_counter:03d}",
                "brand_name": brand_name,
                "med_id": med_id,
                "generic_name": generic_name,  # Denormalized for convenience
                "manufacturer": manufacturer,
                "country": country,
                "unit_price": price,
                "is_innovator": is_innovator,
                "counterfeit_risk": counterfeit_risk,
            }
            brands.append(brand)
            brand_counter += 1

    return brands


# TEST
if __name__ == "__main__":
    from generators.medications import generate_medications

    meds = generate_medications()
    brands = generate_brands(meds)

    # print(f"Generated {len(brands)} brands for {len(meds)} medications")
    # print(f"\nSample brand: {brands[0]}")

# Generated 70 brands for 30 medications
# {'
# brand_id': 'BRD_001',
# 'brand_name': 'Coartem',
# 'med_id': 'MED_001',
# 'generic_name': 'Artemether-Lumefantrine',
# 'manufacturer': 'Novartis',
# 'country': 'Switzerland',
# 'unit_price': 3500, '
# is_innovator': True,
# 'counterfeit_risk': 'HIGH'
# }
