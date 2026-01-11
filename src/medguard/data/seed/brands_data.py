# so to access = brands["Arthemeter-lumefantrine"] which gives a list of tuples
# (brand_name, manufacturer, country, price_ngn, is_innovator, counterfeit_risk)

brands_data = {
    "Artemether-Lumefantrine": [
        ("Coartem", "Novartis", "Switzerland", 3500, True, "HIGH"),
        ("Lokmal", "Emzor Pharmaceutical", "Nigeria", 1700, False, "LOW"),
        ("Combisunate", "Fidson Healthcare", "Nigeria", 1600, False, "LOW"),
    ],
    "Artesunate-Amodiaquine": [
        ("Coarsucam", "Sanofi", "France", 2800, True, "HIGH"),
        ("Larimal", "Emzor Pharmaceutical", "Nigeria", 1400, False, "LOW"),
    ],
    "Artesunate Injection": [
        ("Atesid", "Emzor Pharmaceutical", "Nigeria", 3600, False, "LOW")
    ],
    "Sulfadoxine-Pyrimethamine": [
        ("Fansidar", "Roche", "Switzerland", 800, True, "HIGH"),
        ("Malareich", "Emzor Pharmaceutical", "Nigeria", 400, False, "LOW"),
    ],
    "Amoxicillin": [
        ("Amoxil", "GSK", "UK", 1800, True, "HIGH"),
        ("Ospamox", "Sandoz", "Switzerland", 1500, False, "MEDIUM"),
        ("Fidson Amoxicillin", "Fidson Healthcare", "Nigeria", 800, False, "LOW"),
        ("Promoxil", "Emzor Pharmaceutical", "Nigeria", 700, False, "LOW"),
        ("Moxclav", "May & Baker Nigeria", "Nigeria", 750, False, "LOW"),
    ],
    "Amoxicillin-Clavulanate": [
        ("Augmentin", "GSK", "UK", 4500, True, "HIGH"),
        ("Curam", "Sandoz", "Switzerland", 3500, False, "MEDIUM"),
        ("Klavuxin", "Emzor Pharmaceutical", "Nigeria", 2500, False, "LOW"),
    ],
    "Metronidazole": [
        ("Flagyl", "Sanofi", "France", 1200, True, "HIGH"),
        ("Flagentyl", "May & Baker Nigeria", "Nigeria", 500, False, "LOW"),
        ("Trogyl", "Fidson Healthcare", "Nigeria", 450, False, "LOW"),
        ("Metrozol", "Emzor Pharmaceutical", "Nigeria", 400, False, "LOW"),
    ],
    "Ciprofloxacin": [
        ("Cipro", "Bayer", "Germany", 3000, True, "HIGH"),
        ("Ciprotab", "Fidson Healthcare", "Nigeria", 1200, False, "LOW"),
        ("Cipronol", "Emzor Pharmaceutical", "Nigeria", 1000, False, "LOW"),
    ],
    "Ceftriaxone": [
        ("Rocephin", "Roche", "Switzerland", 5000, True, "HIGH"),
        ("Ceftrizon", "Emzor Pharmaceutical", "Nigeria", 2000, False, "LOW"),
    ],
    "Azithromycin": [
        ("Zithromax", "Pfizer", "USA", 3500, True, "HIGH"),
        ("Forste", "Fidson Healthcare", "Nigeria", 1500, False, "LOW"),
    ],
    "Paracetamol": [
        ("Panadol", "GSK", "UK", 600, True, "HIGH"),
        ("Emzor Paracetamol", "Emzor Pharmaceutical", "Nigeria", 250, False, "LOW"),
        ("M&B Paracetamol", "May & Baker Nigeria", "Nigeria", 280, False, "LOW"),
    ],
    "Ibuprofen": [
        ("Nurofen", "Reckitt", "UK", 850, False, "MEDIUM"),
        ("Ibucap", "Emzor Pharmaceutical", "Nigeria", 400, False, "LOW"),
    ],
    "Diclofenac": [
        ("Voltaren", "Novartis", "Switzerland", 1500, True, "HIGH"),
        ("Zortafen", "Emzor Pharmaceutical", "Nigeria", 600, False, "LOW"),
    ],
    "Amlodipine": [
        ("Norvasc", "Pfizer", "USA", 2500, True, "HIGH"),
        ("Amlod", "Emzor Pharmaceutical", "Nigeria", 800, False, "LOW"),
    ],
    "Lisinopril": [
        ("Zestril", "AstraZeneca", "UK", 2200, True, "HIGH"),
        ("Sinopril", "Fidson Healthcare", "Nigeria", 700, False, "LOW"),
    ],
    "Hydrochlorothiazide": [
        ("Esidrex", "Novartis", "Switzerland", 1000, True, "MEDIUM"),
        ("Hydrozide", "Emzor Pharmaceutical", "Nigeria", 400, False, "LOW"),
    ],
    "Metformin": [
        ("Glucophage", "Merck", "Germany", 2000, True, "HIGH"),
        ("Gluformin", "Emzor Pharmaceutical", "Nigeria", 600, False, "LOW"),
        ("Diabetmin", "Fidson Healthcare", "Nigeria", 650, False, "LOW"),
    ],
    "Glibenclamide": [
        ("Daonil", "Sanofi", "France", 1500, True, "MEDIUM"),
        ("Glimel", "Emzor Pharmaceutical", "Nigeria", 500, False, "LOW"),
    ],
    "Insulin Human Regular": [
        ("Actrapid", "Novo Nordisk", "Denmark", 9000, True, "HIGH"),
    ],
    "Oral Rehydration Salts": [
        ("ORS-WHO", "Emzor Pharmaceutical", "Nigeria", 150, False, "LOW"),
    ],
    "Zinc Sulfate": [
        ("Zinc-ORS", "Emzor Pharmaceutical", "Nigeria", 200, False, "LOW"),
    ],
    "Omeprazole": [
        ("Losec", "AstraZeneca", "UK", 3000, True, "HIGH"),
        ("Omepral", "Emzor Pharmaceutical", "Nigeria", 800, False, "LOW"),
    ],
    "Salbutamol Inhaler": [
        ("Ventolin", "GSK", "UK", 2500, True, "HIGH"),
        ("Salbu", "Emzor Pharmaceutical", "Nigeria", 1200, False, "LOW"),
    ],
    "Prednisolone": [
        ("Predsol", "Sanofi", "France", 1200, True, "MEDIUM"),
        ("Wysolone", "Pfizer", "USA", 1000, False, "MEDIUM"),
        ("Predone", "Emzor Pharmaceutical", "Nigeria", 500, False, "LOW"),
    ],
    "Chlorpheniramine": [
        ("Piriton", "GSK", "UK", 600, True, "MEDIUM"),
        ("Chlor-Trimeton", "Merck", "Germany", 550, False, "MEDIUM"),
        ("Histaphen", "Emzor Pharmaceutical", "Nigeria", 250, False, "LOW"),
        ("Allergex", "Fidson Healthcare", "Nigeria", 280, False, "LOW"),
    ],
    "Ferrous Sulfate + Folic Acid": [
        ("Fefol", "GSK", "UK", 800, True, "MEDIUM"),
        ("Chemiron", "Emzor Pharmaceutical", "Nigeria", 400, False, "LOW"),
        ("Ferobin", "Fidson Healthcare", "Nigeria", 350, False, "LOW"),
    ],
    "Vitamin B Complex": [
        ("Becosules", "Pfizer", "USA", 700, True, "LOW"),
        ("Neurobion", "Merck", "Germany", 800, False, "MEDIUM"),
        ("B-Complex", "Emzor Pharmaceutical", "Nigeria", 250, False, "LOW"),
    ],
    "Levonorgestrel-Ethinylestradiol": [
        ("Microgynon", "Bayer", "Germany", 1500, True, "MEDIUM"),
        ("Levofem", "Pfizer", "USA", 1200, False, "MEDIUM"),
    ],
    "Tenofovir-Lamivudine-Efavirenz": [
        ("Teno", "Emzor Pharmaceutical", "Nigeria", 5000, True, "MEDIUM")
    ],
    "Oxytocin": [
        ("Pitocin", "Pfizer", "USA", 2000, True, "HIGH"),
        ("Syntocinon", "Novartis", "Switzerland", 1800, True, "HIGH"),
    ],
}
