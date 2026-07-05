
# ==================================================
# GENERATOR.PY
# PURPOSE:
# This file creates synthetic transaction data.
# It is not a final decision maker
# It is not the final risk analyzer
#
# OUTPUT
# transactions.csv
#
# Later scripts:
# geo_analyzer -> checks 500 meter coordinate proximity
# analyzer.py  -> ranks accounts and creates risk outputs
# ==================================================

import csv
import random
from datetime import datetime, timedelta

# ==================================================
# BASIC SETTINGS
# ==================================================

random.seed(42)

NUM_ACCOUNTS = 2500
MIN_TX_PER_ACCOUNT = 20
MAX_TX_PER_ACCOUNT = 24

START_DATE = datetime(2025, 1, 1)
ANALYSIS_DAYS = 120

OUTPUT_FILE = "transactions.csv"

MIN_AMOUNT = 70.00
MAX_AMOUNT = 25000.00

GEO_LOCATION_SHARE = 0.25

SUSPICIOUS_MERCHANT_SHARE = 0.30

# ==================================================
# ACCOUNT / TRANSACTION SETTINGS
# ==================================================

PAYMENT_TYPES = [
    "bank_transfer",
    "paypal",
    "cashapp",
    "venmo",
    "remittance",
    "brokerage_transfer",
    "equity_trade",
    "crypto_exchange",
    "derivatives_trade",
]

MARKETS = [
    "NYSE",
    "NASDAQ",
    "LSE",
    "HKEX",
    "SSE",
    "TSX",
    "JPX",
    "Euronext",
]

COUNTRIES = [
    "US",
    "US",
    "US",
    "CA",
    "MX",
    "CN",
    "HK"
]

# ==================================================
# MERCHANT / ENTITY TYPES
#
# These are synthetic merchant labels based on FinCEN/Treasury
# typology categories
#
# Do NOT write theses as proof of criminal activity.
# They are open-source risk categories for the purpose of
# Sumerau Toole's project: Center of Gravity Finder
# ==================================================

NORMAL_MERCHANTS = [
    ("Tampa Grocery Market", "normal_retail"),
    ("Everyday Fuel Stop", "normal_fuel"),
    ("Suncoast Hardware", "hardware"),
    ("Campus Book Supply", "education_retail"),
    ("Mobile Phone Payment", "personal_transfer"),
    ("Online Marketplace Store", "ecommerce"),
    ("General Logistics LLC", "logistics"),
    ("Restaurant Services Group", "restaurant"),
    ("Small Business Consulting", "consulting"),
    ("Auto Parts Warehouse", "auto_parts")
]

RISK_MERCHANTS = [
    ("PRC Chemical Supply Trading", "chemical_supplier_prc"),
    ("Online Chemical Vendor", "ecommerce_chemical_vendor"),
    ("Chemical Import Services", "chemical_importer"),
    ("Mexico Chemical Broker", "chemical_broker_mx"),
    ("Front Company Holdings", "front_shell_company"),
    ("Fuel Transport Services", "fuel_transport"),
    ("Retail Gas Holdings", "fuel_company"),
    ("Oilfield Waste Transport", "hazardous_material_transport"),
    ("Cross Border Logistics Group", "cross_border_logistics"),
    ("Construction Materials Export", "construction"),
    ("Hardware Bulk Supply", "hardware"),
    ("Marketing Services LLC", "possible_front_business"),
    ("Money Mule Transfer", "money_mule_straw_buyer")
]


# ------------------------------------------------------------
# MEMO OPTIONS
#
# These are fake transaction memo lines.
# Some are normal.
# Some are suspicious-looking but still synthetic.
# ------------------------------------------------------------

NORMAL_MEMOS = [
    "invoice payment",
    "monthly services",
    "equipment purchase",
    "retail purchase",
    "consulting fee",
    "shipping payment",
    "student expense",
    "fuel purchase",
    "restaurant supply order",
    "online order"
]

RISK_MEMOS = [
    "chemical sample invoice",
    "bulk supply payment",
    "cross-border freight",
    "fuel transport fee",
    "industrial solvent order",
    "brokerage services",
    "misc import fee",
    "warehouse transfer",
    "logistics handling",
    "hazardous materials transport"
]

# ==================================================
# EXACT GEO REFERENCE LOCATIONS
# These coordinates have been derived from FinCEN reporting
#
# Later, geo_analyzer.py checks whether a transaction is within
# 500 meters of these locations
# ==================================================

GEO_LOCATIONS = [
{
"location_id": "GEO001",
"address": "111 Jalnidhi Complex, Opp. Bahumali Building, Surat, Gujarat 395001",
"latitude": 28.21473,
"longitude": 82.30206,
"category": "international_business_location"
},
{
"location_id": "GEO002",
"address": "Bridge of the Americas Port Entry, El Paso, TX",
"latitude": 31.7588,
"longitude": -106.4508,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO003",
"address": "Lincoln/Juarez Bridge, Laredo, TX",
"latitude": 27.506748,
"longitude": -99.502914,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO004",
"address": "5900 Highway 225, Deer Park, TX",
"latitude": 29.7112416,
"longitude": -95.12136,
"category": "oil_refinery_or_fuel_location"
},
{
"location_id": "GEO005",
"address": "Avenida Marina Nacional No 329, Miguel Hidalgo, Ciudad de Mexico",
"latitude": 19.439522,
"longitude": -99.174929,
"category": "mexico_business_location"
},
{
"location_id": "GEO006",
"address": "Av Central 450, Reynosa, Tamaulipas",
"latitude": 26.06173,
"longitude": -98.33199,
"category": "tamaulipas_texas_corridor"
},
{
"location_id": "GEO007",
"address": "Blvd Dolores del Rio No. 704, Queretaro",
"latitude": 20.571957,
"longitude": -100.419806,
"category": "mexico_business_location"
},
{
"location_id": "GEO008",
"address": "PRC Corridor to Sinaloa, Mexico Corridor",
"latitude": 24.997812,
"longitude": -107.477936,
"category": "sinaloa_fentanyl_corridor"
},
{
"location_id": "GEO009",
"address": "4215 Ketcham Street, Elmhurst, NY",
"latitude": 40.744777,
"longitude": -73.882036,
"category": "us_intermediary_or_business_node"
},
{
"location_id": "GEO010",
"address": "Hebei Blvd, Zhengding, Shijiazhuang, Hebei, China",
"latitude": 38.120247,
"longitude": 114.59876,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO011",
"address": "Yanking Blvd, Jiangtan, Jiang'an District, Wuhan, China",
"latitude": 30.592772,
"longitude": 114.305249,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO012",
"address": "Henan Ruiju Biotechnology, Zhengzhou, Henan, China",
"latitude": 34.747197,
"longitude": 113.625352,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO013",
"address": "Xiamen Section, China Pilot Free Trade Zone",
"latitude": 36.559372,
"longitude": 103.753349,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO014",
"address": "Anliang Dongyi Financial Plaza, Hefei, Anhui, China",
"latitude": 38.878719,
"longitude": 117.264969,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO015",
"address": "Hanhong Medicine Technology Company, Wuhan, China",
"latitude": 30.59276,
"longitude": 114.305252,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO016",
"address": "Jiangsu Bangdeya New Material Technology Company, Changzhou, China",
"latitude": 31.678426,
"longitude": 120.297171,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO017",
"address": "216 Zhongshan East Rd, Shijiazhuang, Hebei, China",
"latitude": 38.042333,
"longitude": 114.514778,
"category": "prc_precursor_chemical_zone"
},
{
"location_id": "GEO018",
"address": "Rancho la Lagunita, Mezquital, Durango",
"latitude": 22.472336,
"longitude": -104.418425,
"category": "cartel_regional_risk_location"
},
{
"location_id": "GEO019",
"address": "Tamazula de Gordiano, Jalisco, Mexico",
"latitude": 19.67639,
"longitude": -103.25,
"category": "cartel_regional_risk_location"
},
{
"location_id": "GEO020",
"address": "Badiraguato, Sinaloa, Mexico",
"latitude": 23.376621,
"longitude": -107.557952,
"category": "sinaloa_fentanyl_corridor"
},
{
"location_id": "GEO021",
"address": "Bachigualato, Culiacan, Sinaloa",
"latitude": 24.767176,
"longitude": -107.469468,
"category": "sinaloa_fentanyl_corridor"
},
{
"location_id": "GEO022",
"address": "Refineria Lazaro Cardenas del Rio, Minatitlan, Veracruz",
"latitude": 17.97986,
"longitude": -94.52695,
"category": "veracruz_fuel_hub"
},
{
"location_id": "GEO023",
"address": "Altamira, Tamaulipas, Mexico",
"latitude": 22.492463,
"longitude": -97.896251,
"category": "oil_smuggling_corridor"
},
{
"location_id": "GEO024",
"address": "Cadereyta Jimenez, Nuevo Leon, Mexico",
"latitude": 25.58726,
"longitude": -99.94226,
"category": "oil_smuggling_corridor"
},
{
"location_id": "GEO025",
"address": "2350 N Sam Houston Parkway East, Houston, TX",
"latitude": 29.938874,
"longitude": -95.350767,
"category": "us_intermediary_or_business_node"
},
{
"location_id": "GEO026",
"address": "7141 Office City Dr, Houston, TX",
"latitude": 29.701514,
"longitude": -95.291167,
"category": "us_intermediary_or_business_node"
},
{
"location_id": "GEO027",
"address": "PRC to Sinaloa Corridor",
"latitude": 24.997812,
"longitude": -107.477936,
"category": "sinaloa_fentanyl_corridor"
},
{
"location_id": "GEO028",
"address": "Juarez, Chihuahua, Mexico",
"latitude": 31.669241,
"longitude": -106.337439,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO029",
"address": "Manzanillo, Colima, Mexico",
"latitude": 19.0504,
"longitude": -104.317156,
"category": "oil_smuggling_corridor"
},
{
"location_id": "GEO030",
"address": "Lazaro Cardenas, Michoacan, Mexico",
"latitude": 17.967338,
"longitude": -102.202131,
"category": "oil_smuggling_corridor"
},
{
"location_id": "GEO031",
"address": "Bay of Campeche, Veracruz, Mexico",
"latitude": 19.218419,
"longitude": -96.158742,
"category": "veracruz_fuel_hub"
},
{
"location_id": "GEO032",
"address": "Veracruz de Ignacio de la Llave, Mexico",
"latitude": 19.22570,
"longitude": -96.15358,
"category": "veracruz_fuel_hub"
},
{
"location_id": "GEO033",
"address": "Matamoros, Tamaulipas, Mexico",
"latitude": 25.84612,
"longitude": -97.50925,
"category": "tamaulipas_texas_corridor"
},
{
"location_id": "GEO034",
"address": "Heroica Matamoros, Tamaulipas, Mexico",
"latitude": 25.83384,
"longitude": -97.51003,
"category": "tamaulipas_texas_corridor"
},
{
"location_id": "GEO035",
"address": "Brownsville, TX",
"latitude": 25.94442,
"longitude": -97.40621,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO036",
"address": "San Ysidro Blvd, San Diego, CA",
"latitude": 32.555872,
"longitude": -117.051854,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO037",
"address": "Paseo International South, San Diego, CA",
"latitude": 32.550849,
"longitude": -116.938258,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO038",
"address": "Mexicali, Baja California, Mexico",
"latitude": 32.663575,
"longitude": -115.468956,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO039",
"address": "San Luis, AZ",
"latitude": 32.48591,
"longitude": -114.78195,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO040",
"address": "Nogales, AZ",
"latitude": 31.33529,
"longitude": -110.96712,
"category": "border_crossing_or_port_entry"
},
{
"location_id": "GEO041",
"address": "Manzanillo, Colima, Mexico",
"latitude": 19.07253,
"longitude": -104.29014,
"category": "oil_smuggling_corridor"
},
{
"location_id": "GEO042",
"address": "Lazaro Cardenas Port, Michoacan, Mexico",
"latitude": 17.94141,
"longitude": -102.18780,
"category": "oil_smuggling_corridor"
}
]


# ============================================================
# HELPER FUNCTION: CREATE ACCOUNT IDS
# Example: ACCT00001
# ============================================================

def create_transaction_id(transaction_counter):
    return "TX" + str(transaction_counter).zfill(7)


# ============================================================
# HELPER FUNCTION: CREATE RANDOM DATE
# Creates a random date inside the 120-day analysis window.
# ============================================================

def get_random_date():
    random_days = random.randint(0, ANALYSIS_DAYS -1)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0,59)

    transaction_date = START_DATE + timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes
    )

    return transaction_date

# ============================================================
# HELPER FUNCTION: CHOOSE MERCHANT
# Sometimes chooses a normal merchant.
# Sometimes chooses a risk-category merchant.
# ============================================================

def choose_merchant():
    use_risk_merchant = random.random() < SUSPICIOUS_MERCHANT_SHARE

    if use_risk_merchant:
        merchant_name, merchant_type = random.choice(RISK_MERCHANTS)
        memo = random.choice(RISK_MEMOS)
    else:
        merchant_name, merchant_type = random.choice(NORMAL_MERCHANTS)
        memo = random.choice(NORMAL_MEMOS)

    return merchant_name, merchant_type, memo

# ============================================================
# HELPER FUNCTION: CHOOSE GEO LOCATION
#
# Some transactions use one of the exact reference coordinates.
# Other transactions use a random normal coordinate.
# ============================================================

def choose_geo_location(country):
    use_reference_location = random.random() < GEO_LOCATION_SHARE

    if use_reference_location:
        location = random.choice(GEO_LOCATIONS)

        base_lat = location["latitude"]
        base_lon = location["longitude"]

        geo_roll = random.random()

        if geo_roll < 0.25:
            offset = 0.004
            geo_distance_band = "under_500m"

        elif geo_roll < 0.50:
            offset = 0.009
            geo_distance_band = "501_1000m"

        elif geo_roll < 0.75:
            offset = 0.015
            geo_distance_band = "1001_1599m"

        else:
            offset = 0.019
            geo_distance_band = "1600_1800m"

        latitude = round(base_lat + random.uniform(-offset, offset), 6)
        longitude = round(base_lon + random.uniform(-offset, offset), 6)


        location_id = location["location_id"]
        location_address = location["address"]
        location_category = location["category"]

    else:
        location_id = "NONE"
        location_address = "Normal non-reference transaction location"
        location_category = "normal_location"
        geo_distance_band = "outside_1800m"

        if country == "US":
            latitude = round(random.uniform(25.0, 41.0), 6)
            longitude = round(random.uniform(-120.0, -73.0), 6)

        elif country == "MX":
            latitude = round(random.uniform(17.0, 32.0), 6)
            longitude = round(random.uniform(-117.0, -86.0), 6)

        elif country == "CN":
            latitude = round(random.uniform(22.0, 40.0), 6)
            longitude = round(random.uniform(103.0, 122.0), 6)

        elif country == "HK":
            latitude = round(random.uniform(22.1, 22.5), 6)
            longitude = round(random.uniform(113.8, 114.4), 6)

        else:
            latitude = round(random.uniform(20.0, 45.0), 6)
            longitude = round(random.uniform(-120.0, -70.0), 6)

    return (
        location_id,
        location_address,
        latitude,
        longitude,
        location_category,
        geo_distance_band
    )


# ============================================================
# HELPER FUNCTION: CHOOSE MARKET
# Only applies to market-related payment types.
# ============================================================

def choose_market(payment_type):
    if payment_type in [
        "brokerage_transfer",
        "equity_trade",
        "derivatives_trade"
    ]:
        return random.choice(MARKETS)
    else:
        return "NONE"


# ============================================================
# HELPER FUNCTION: CHOOSE AMOUNT
#
# This creates mostly smaller transactions but allows some larger
# suspicious-looking values.
# ============================================================

def choose_amount(merchant_type):
    if merchant_type in [
        "chemical_supplier_prc",
        "ecommerce_chemical_vendor",
        "chemical_importer",
        "chemical_broker_mx",
        "fuel_transport",
        "fuel_company",
        "hazardous_material_transport",
        "cross_border_logistics"
    ]:
        amount = random.uniform(2500.00, MAX_AMOUNT)

    else:
        amount = random.uniform(MIN_AMOUNT, 8500.00)

    return round(amount, 2)


# ============================================================
# HELPER FUNCTION: CREATE ONE TRANSACTION
# ============================================================

def create_transaction(transaction_counter, sender_account, receiver_account):
    transaction_id = create_transaction_id(transaction_counter)

    transaction_date = get_random_date()
    payment_type = random.choice(PAYMENT_TYPES)
    country = random.choice(COUNTRIES)

    merchant_name, merchant_type, memo = choose_merchant()
    amount = choose_amount(merchant_type)

    location_id, location_address, latitude, longitude, location_category, geo_distance_band = choose_geo_location(country)

    market = choose_market(payment_type)

    sender_lat = round(random.uniform(17.0, 41.0), 6)
    sender_lon = round(random.uniform(-118.0, -73.0), 6)

    receiver_lat = round(random.uniform(17.0, 41.0), 6)
    receiver_lon = round(random.uniform(-118.0, -73.0), 6)

    geo_roll = random.random()

    if geo_roll < 0.25:
        geo_distance_band = "under_500m"
        geo_risk_points = 10
    elif geo_roll < 0.50:
        geo_distance_band = "between_501_1000m"
        geo_risk_points = 7
    elif geo_roll < 0.75:
        geo_distance_band = "between_1001_1599m"
        geo_risk_points = 3
    elif geo_roll < 0.90:
        geo_distance_band = "between_1600_1800m"
        geo_risk_points = 2
    else:
        geo_distance_band = "outside_1800m"
        geo_risk_points = 0

    transaction = {
        "transaction_id": transaction_id,
        "sender": sender_account,
        "receiver": receiver_account,
        "amount": amount,
        "payment_type": payment_type,
        "geo_flag": 1 if location_id != "NONE" else 0,
        "sender_country": country,
        "receiver_country": country,
        "sender_city": location_address,
        "receiver_city": location_address,
        "route_corridor": location_category,
        "sender_lat": sender_lat,
        "sender_lon": sender_lon,
        "receiver_lat": receiver_lat,
        "receiver_lon": receiver_lon,
        "date": transaction_date.strftime("%Y-%m-%d"),
        "datetime_group": transaction_date.strftime("%Y-%m-%d %H:%M"),
        "merchant_name": merchant_name,
        "merchant_type": merchant_type,
        "country": country,
        "market": market,
        "geo_distance_band": geo_distance_band,
        "geo_risk_points": geo_risk_points,
        "latitude": latitude,
        "longitude": longitude,
        "location_id": location_id,
        "location_address": location_address,
        "location_category": location_category,
        "memo": memo
    }

    return transaction


# ============================================================
# MAIN FUNCTION: GENERATE ALL TRANSACTION
# ============================================================

def create_accounts(num_accounts):
    accounts = []

    for i in range(1, num_accounts +1):
        account_id = "ACCT" + str(i).zfill(5)
        accounts.append(account_id)

    return accounts

def generate_transactions():
    accounts = create_accounts(NUM_ACCOUNTS)
    transactions = []

    transaction_counter = 1

    for sender_account in accounts:
        number_of_transactions = random.randint(
        MIN_TX_PER_ACCOUNT,
        MAX_TX_PER_ACCOUNT
    )

        for count in range(number_of_transactions):
            receiver_account = random.choice(accounts)

# Prevent sender and receiver from being the same account.
            while receiver_account == sender_account:
                receiver_account = random.choice(accounts)

        transaction = create_transaction(
            transaction_counter,
            sender_account,
            receiver_account
        )

        transactions.append(transaction)
        transaction_counter += 1

    return transactions


# ============================================================
# SAVE TO CSV
# ============================================================

def save_transactions_to_csv(transactions):

    fieldnames = [
        "transaction_id",
        "sender",
        "receiver",
        "amount",
        "sender_lat",
        "sender_lon",
        "receiver_lat",
        "receiver_lon",
        "date",
        "datetime_group",
        "payment_type",
        "geo_flag",
        "sender_country",
        "receiver_country",
        "sender_city",
        "receiver_city",
        "route_corridor",
        "merchant_name",
        "merchant_type",
        "country",
        "market",
        "geo_distance_band",
        "geo_risk_points",
        "latitude",
        "longitude",
        "location_id",
        "location_address",
        "location_category",
        "memo"
    ]

    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for transaction in transactions:
            writer.writerow(transaction)

# ============================================================
# PROGRAM START
# ============================================================

def main():
    transactions = generate_transactions()
    save_transactions_to_csv(transactions)

    total_amount = 0

    for transaction in transactions:
        total_amount += float(transaction["amount"])

    print("Synthetic transaction file created successfully.")
    print("Output file:", OUTPUT_FILE)
    print("Total transactions:", len(transactions))
    print("Total transaction amount: $", round(total_amount, 2))
    print("Number of accounts:", NUM_ACCOUNTS)
    print("Analysis window days:", ANALYSIS_DAYS)
    print("Geo reference location share:", GEO_LOCATION_SHARE)
    print("Suspicious merchant share:", SUSPICIOUS_MERCHANT_SHARE)


if __name__ == "__main__":
    main()


