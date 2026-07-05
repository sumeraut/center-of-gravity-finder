import csv
import math

STRONG_RADIUS_METERS = 500
MEDIUM_RADIUS_METERS = 1000

UNDER_500_SCORE = 10
RANGE_501_1000_SCORE = 7
RANGE_1001_1599_SCORE = 3
RANGE_1600_1800_SCORE = 2

STRONG_GEO_SCORE = 2
MEDIUM_GEO_SCORE = 1
OUTER_GEO_SCORE = 0.5

REPORT_COORDS = [
    ("El Paso Bridge of Americas", 31.7588, 106.4508),
    ("Laredo Lincoln/Juarez Bridge", 27.506748, -99.502914),
    ("Deer Park TX", 29.7112416, -95.12136),
    ("Mexico City Marina Nacional", 19.439522, -99.174929),
    ("Reynosa Tamaulipas", 26.06173, -98.33199),
    ("PRC to Sinaloa Corridor", 24.997812, -107.477936),
    ("Elmhurst NY", 40.744777, -73.882036),
    ("Wuhan China", 30.592772, 114.305249),
    ("Zhengzhou Henan China", 34.747197, 113.625352),
    ("Brownsville TX", 25.94442, -97.40621),
    ("San Ysidro CA", 32.555872, -117.051854),
    ("Yuma AZ", 32.72853, -114.62064),
    ("Nogales AZ", 31.33529, -110.96712),
    ("San Luiz AZ", 32.48591, -114.78195),
    ("Manzanillo Port Area", 19.07253, -104.29014),
    ("Lazaro Cardenas Port", 17.94141, -102.18780),
    ("Veracruz Port Area", 19.22570, -96.15358),
    ("Matamoros Tamaulipas", 25.84612, -97.896251),
    ("Culiacan Sinaloa", 24.767176, -107.469469),
    ("Altamira Tamaulipas", 22.492463,  -97.896251),
    ("Cadereyta Nuevo Leon", 25.58726, -99.94226),
    ("Houston Sam Houston Parkway", 29.938874, -95.350767),
    ("Ciudad Juarez Chihuahua", 31.669241, -106.337439),
    ("Mexicali Baja California", 32.663575, -115.468956),
    ("Otay Mesa San Diego", 32.550849, -116.938258)
]

def haversine_meters(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c

def get_geo_range(distance):

    if distance <= STRONG_RADIUS_METERS:
        return "under_500m"

    elif distance <= MEDIUM_RADIUS_METERS:
        return "between_501_1000m"

    elif 1001 <= distance <= 1599:
        return "between_1001_1599"

    elif 1600 <= distance <= 1800:
        return "between_1600_1800m"

    else:
        return "outside_geo_range"

def geo_analyze_transactions(input_file):
    enriched_rows = []

    with open(input_file, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["geo_flag"] = 0
            row["geo_location"] = ""
            row["geo_distance_m"] = ""
            row["geo_match_type"] = ""
            row["geo_range"] = ""

            geo_range = row.get("geo_distance_band", "")
            geo_points = int(row.get("geo_risk_points", 0))

            row["geo_range"] = geo_range
            row["geo_distance_m"] = ""
            row["geo_match_type"] = "generator_band"
            row["geo_location"] = row.get("location_address", "")

            if geo_points > 0:
                row["geo_flag"] = 1
            else:
                row["geo_flag"] = 0

            enriched_rows.append(row)

    return enriched_rows

def build_geo_risk_accounts(enriched_rows):
    accounts = {}

    for row in enriched_rows:
        sender = row["sender"]
        receiver = row["receiver"]
        geo_flag = int(row["geo_flag"])
        geo_range = row["geo_range"]

        if sender not in accounts:
            accounts[sender] = {
                "geo_match_count": 0,
                "geo_under_500_count": 0,
                "geo_between_501_1000_count": 0,
                "geo_between_1001_1599_count": 0,
                "geo_between_1600_1800_count": 0,
                "geo_proximity_score": 0,
                "connections": set(),
                "matched_locations": set(),
                "merchant_values": set(),
                "memo_values": set()
            }

        if receiver not in accounts:
            accounts[receiver] = {
                "geo_match_count": 0,
                "geo_under_500_count": 0,
                "geo_between_501_1000_count": 0,
                "geo_between_1001_1599_count": 0,
                "geo_between_1600_1800_count": 0,
                "geo_proximity_score": 0,
                "connections": set(),
                "matched_locations": set(),
                "merchant_values": set(),
                "memo_values": set()
            }

        accounts[sender]["connections"].add(receiver)
        accounts[receiver]["connections"].add(sender)

        merchant = row.get("merchant", "")
        memo = row.get("memo", "")
        geo_location = row.get("geo_location", "")

        if merchant:
            accounts[sender]["merchant_values"].add(merchant)
            accounts[receiver]["merchant_values"].add(merchant)

        if memo:
            accounts[sender]["memo_values"].add(memo)
            accounts[receiver]["memo_values"].add(memo)

        if geo_flag == 1:
            accounts[sender]["geo_match_count"] += 1
            accounts[receiver]["geo_match_count"] += 1

            if geo_location:
                accounts[sender]["matched_locations"].add(geo_location)
                accounts[receiver]["matched_locations"].add(geo_location)

            if geo_range == "under_500m":
                accounts[sender]["geo_under_500_count"] += 1
                accounts[receiver]["geo_under_500_count"] += 1

                accounts[sender]["geo_proximity_score"] += UNDER_500_SCORE
                accounts[receiver]["geo_proximity_score"] += UNDER_500_SCORE

            if geo_range == "between_501_1000m":
                accounts[sender]["geo_between_501_1000_count"] += 1
                accounts[receiver]["geo_between_501_1000_count"] += 1

                accounts[sender]["geo_proximity_score"] += RANGE_501_1000_SCORE
                accounts[receiver]["geo_proximity_score"] += RANGE_501_1000_SCORE

            if geo_range == "between_1001_1599m":
                accounts[sender]["geo_between_1001_1599_count"] += 1
                accounts[receiver]["geo_between_1001_1599_count"] += 1

                accounts[sender]["geo_proximity_score"] += RANGE_1001_1599_SCORE
                accounts[receiver]["geo_proximity_score"] += RANGE_1001_1599_SCORE


            if geo_range == "between_1600_1800m":
                accounts[sender]["geo_between_1600_1800_count"] += 1
                accounts[receiver]["geo_between_1600_1800_count"] += 1

                accounts[sender]["geo_proximity_score"] += RANGE_1600_1800_SCORE
                accounts[receiver]["geo_proximity_score"] += RANGE_1600_1800_SCORE

    return accounts

# ============================================================
# EXPORT ENRICHED TRANSACTIONS
# Creates a transaction CSV with new geo columns:
# - geo_flag
# - geo_location
# - geo_distance_meters
# - geo_match_type
# - geo_range
# ============================================================

def export_geo_enriched_transactions(enriched_rows):
    with open("geo_enriched_transactions.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=enriched_rows[0].keys())
        writer.writeheader()
        writer.writerows(enriched_rows)

def export_geo_risk_accounts(accounts):
    with open("geo_risk_accounts.csv", "w", newline= "") as file:
        writer = csv.writer(file)

        writer.writerow([
            "account_id",
            "geo_match_count",
            "geo_under_500_count",
            "geo_between_501_1000_count",
            "geo_between_1001_1599_count",
            "geo_between_1600_1800_count",
            "geo_proximity_score",
            "connections",
            "matched_locations",
            "merchant_values",
            "memo_values"
        ])

        for account_id, data in accounts.items():
            writer.writerow([
                account_id,
                data["geo_match_count"],
                data["geo_under_500_count"],
                data["geo_between_501_1000_count"],
                data["geo_between_1001_1599_count"],
                data["geo_between_1600_1800_count"],
                data["geo_proximity_score"],
                len(data["connections"]),
                "; ".join(data["matched_locations"]),
                len(data["merchant_values"]),
                len(data["memo_values"])
            ])

enriched_rows = geo_analyze_transactions("transactions.csv")
geo_accounts = build_geo_risk_accounts(enriched_rows)

export_geo_enriched_transactions(enriched_rows)
export_geo_risk_accounts(geo_accounts)

print("Geo analyzer complete.")
print("Files created:")
print("- geo_enriched_transactions.csv")
print("- geo_risk_accounts.csv")
print



