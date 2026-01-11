from medguard.data.seed.facilities_data import facilities_data


def generate_facilities():
    facilities = []

    for i, (
        name,
        facility_type,
        city,
        state,
        tier,
        has_cold_storage,
        latitude,
        longitude,
    ) in enumerate(facilities_data):

        facility = {
            "facility_id": f"FAC_{i+1:03d}",
            "name": name,
            "facility_type": facility_type,
            "city": city,
            "state": state,
            "tier": tier,
            "has_cold_storage": has_cold_storage,
            "latitude": latitude,
            "longitude": longitude,
        }
        facilities.append(facility)

    return facilities


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    facilities = generate_facilities()
    print(f"Generated {len(facilities)} facilities")
    # print(f"\nSample: {facilities[0]}")

# Generated 50 facilities
"""{
    'facility_id': 'FAC_001', ''
    'name': 'Lagos University Teaching Hospital', 
    'facility_type': 'TEACHING_HOSPITAL', 
    'city': 'Idi-Araba', 
    'state': 'Lagos', 
    'tier': 'MAJOR', 
    'has_cold_storage': True, 
    'latitude': 6.5172, 
    'longitude': 3.3549
}"""
