"""
Company types:
- International manufacturers (need Nigerian importer)
- Nigerian manufacturers (can self-distribute) and they often play multiple roles like importing and distributing
- Nigerian importers/distributors (bring in international products)
"""

companies_data = [
    # international manufacturerers: manufacture but need nigerian importers to bring products in
    # (name, country, city, is_manufacturer, is_importer, is_distributor)
    ("Novartis", "Switzerland", "Basel", True, False, False),
    ("GSK", "UK", "London", True, False, False),
    ("Sanofi", "France", "Paris", True, False, False),
    ("Pfizer", "USA", "New York", True, False, False),
    ("Novo Nordisk", "Denmark", "Copenhagen", True, False, False),
    ("Bayer", "Germany", "Leverkusen", True, False, False),
    ("Roche", "Switzerland", "Basel", True, False, False),
    ("AstraZeneca", "UK", "Cambridge", True, False, False),
    ("Merck", "Germany", "Darmstadt", True, False, False),
    ("Sandoz", "Switzerland", "Basel", True, False, False),
    ("Reckitt", "UK", "Slough", True, False, False),
    # nigerian manufacturers/importers/distributors: manufacture their own products but ccan also import for international brands
    ("Emzor Pharmaceutical", "Nigeria", "Lagos", True, True, True),
    ("Fidson Healthcare", "Nigeria", "Lagos", True, True, True),
    ("May & Baker Nigeria", "Nigeria", "Lagos", True, True, True),
    ("Swiss Pharma Nigeria", "Nigeria", "Lagos", True, True, True),
    ("Drugfield Pharmaceuticals", "Nigeria", "Sango Otta", True, True, True),
    ("Afrab-Chem", "Nigeria", "Lagos", True, False, False),
    ("WWCVL", "Nigeria", "Lagos", False, True, True),
    ("Phillips Pharmaceuticals", "Nigeria", "Lagos", True, True, True),
    (
        "New Heights Pharma",
        "Nigeria",
        "Lagos",
        True,
        False,
        True,
    ),
]

authorized_importers = {
    "Novartis": ["WWCVL", "Phillips Pharmaceuticals"],
    "GSK": ["WWCVL"],
    "Pfizer": ["WWCVL"],
    "Novo Nordisk": ["WWCVL"],
    "Sanofi": ["WWCVL", "Phillips Pharmaceuticals"],
    "AstraZeneca": ["WWCVL"],
    "Bayer": ["WWCVL", "Phillips Pharmaceuticals"],
    "Roche": ["WWCVL"],
    "Merck": ["WWCVL"],
    "Sandoz": ["WWCVL"],
}


def generate_companies():
    """Generate company from companies_data."""
    companies = []
    for i, (
        name,
        country,
        city,
        is_manufacturer,
        is_importer,
        is_distributor,
    ) in enumerate(companies_data):
        company = {
            "company_id": f"COMP_{i+1:03d}",
            "name": name,
            "country": country,
            "city": city,
            "is_manufacturer": is_manufacturer,
            "is_importer": is_importer,
            "is_distributor": is_distributor,
        }
        companies.append(company)
    return companies


if __name__ == "__main__":
    companies = generate_companies()
    # print(f"Generated {len(companies)} companies")
    # print(f"\nSample batch: {companies[0]}")


"""{
    "company_id": "COMP_001",
    "name": "Novartis",
    "country": "Switzerland",
    "city": "Basel",
    "is_manufacturer": True,
    "is_importer": False,
    "is_distributor": False,
}
"""
