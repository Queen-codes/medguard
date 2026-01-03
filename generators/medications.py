from medications_data import medications_data


def generate_medications():
    """Generate a medication from medications_data."""
    medications = []
    for i, (
        generic_name,
        therapeutic_class,
        stocking_level,
        is_cold_chain,
        base_demand,
        form,
        category,
        strength,
    ) in enumerate(medications_data):

        medication = {
            "med_id": f"MED_{i+1:03d}",
            "generic_name": generic_name,
            "therapeutic_class": therapeutic_class,
            "stocking_level": stocking_level,
            "form": form,
            "strength": strength,
            "base_demand": base_demand,
            "category": category,
            "is_cold_chain": is_cold_chain,
        }
        medications.append(medication)
    return medications


if __name__ == "__main__":
    meds = generate_medications()
    print(f"Generated {len(meds)} medications")
    print(f"{meds[0]}")

# format structure
"""{
    "med_id": "MED_001",
    "generic_name": "Artemether-Lumefantrine",
    "therapeutic_class": "Antimalarial",
    "stocking_level": 1,
    "form": "pack",
    "strength": "20mg/120mg",
    "base_demand": 200,
    "category": "CRITICAL",
    "is_cold_chain": False,
}
"""
