from datetime import datetime
import csv

class Transaction:
    def __init__(self, row):
        self.tx_id = row["transaction_id"]
        self.sender = row["sender"]
        self.receiver = row["receiver"]
        self.amount = float(row["amount"])
        self.date = row["date"]
        self.date_obj = datetime.strptime(row["date"], "%Y-%m-%d")
        self.payment_type = row["payment_type"]
        self.market = row["market"]
        self.flag = int(row.get("geo_flag", 0))
        self.geo_flag = self.flag
        self.latitude = float(row["latitude"])
        self.longitude = float(row["longitude"])
        self.merchant_name = row.get("merchant_name", "")
        self.merchant_type = row.get("merchant_type", "")
        self.location_address = row.get("location_address", "")
        self.location_category = row.get("location_category", "")
        self.geo_distance_band = row.get("geo_distance_band", "")
        self.geo_risk_points = int(row.get("geo_risk_points", 0))
        self.sender_country = row["sender_country"]
        self.receiver_country = row["receiver_country"]
        self.sender_city = row["sender_city"]
        self.receiver_city = row["receiver_city"]
        self.route = row["route_corridor"]
        self.memo = row["memo"]
        self.risk_score = 0

class Account:
    def __init__(self, account_id):
        self.account_id = account_id
        self.sent_transactions = []
        self.received_transactions = []
        self.connected_accounts = set()
        self.risk_score = 0
        self.hop_count = 0
        self.max_hop_depth = 0
        self.multi_hop_count = 0
        self.time_window_flag = 0
        self.avg_latitude = 0
        self.avg_longitude = 0
        self.merchants = set()
        self.risky_merchants = set()
        self.locations = set()
        self.geo_distance_bands = set()
        self.two_way_activity_flag = 0
        self.reasons = []

def load_transactions(filename):
    transactions = []

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tx = Transaction(row)
            transactions.append(Transaction(row))

    return transactions

def build_accounts(transactions):
    accounts = {}

    for tx in transactions:
        if tx.sender not in accounts:
            accounts[tx.sender] = Account(tx.sender)

        if tx.receiver not in accounts:
            accounts[tx.receiver] = Account(tx.receiver)

        accounts[tx.sender].sent_transactions.append(tx)
        accounts[tx.receiver].received_transactions.append(tx)

        accounts[tx.sender].connected_accounts.add(tx.receiver)
        accounts[tx.receiver].connected_accounts.add(tx.sender)

    return accounts


def score_transactions(transactions):
    for tx in transactions:
        score = 0

        if tx.amount > 10000:
            score += 1

        if tx.payment_type in ["bank_transfer", "wire_transfer", "brokerage_transfer"]:
            score += 1

        if tx.flag != "normal":
            score += 1

        if tx.route != "Domestic US Transfer":
            score += 1

        if tx.sender_country != "US" or tx.receiver_country != "US":
            score += 1

        suspicious_words = [
            "chemical",
            "fuel",
            "routing",
            "brokerage",
            "layered",
            "cash",
            "petroleum",
            "shipment"
        ]

        for word in suspicious_words:
            if word in tx.memo.lower():
                score += 1
                break

        if tx.flag == 1:
            score += 2

        tx.risk_score = score

def count_hops(accounts):
    for acc in  accounts.values():
        if len(acc.sent_transactions) > 0 and len(acc.received_transactions) > 0:
            acc.hop_count =  min(
                len(acc.sent_transactions),
                len(acc.received_transactions)
            )
        else:
            acc.hop_count = 0

def calculate_hop_depth(accounts):
    for acc in accounts.values():
        max_depth = 0
        chain_count = 0

        for tx1 in acc.received_transactions:
            B = acc.account_id

            for tx2 in acc.sent_transactions:
                C = tx2.receiver

                if C in accounts:
                    max_depth = max(max_depth, 3)
                    chain_count += 1

                    for tx3 in accounts[C].sent_transactions:
                        D = tx3.receiver

                        if D in accounts:
                            max_depth = max(max_depth, 4)
                            chain_count += 1

                            for tx4 in accounts[D].sent_transactions:
                                E = tx4.receiver

                                if E in accounts:
                                    max_depth = max(max_depth, 5)
                                    chain_count += 1

        acc.max_hop_depth = max_depth
        acc.multi_hop_count = chain_count

def score_accounts(accounts):
    for acc in accounts.values():
        score = 0

        total_sent = sum(tx.amount for tx in acc.sent_transactions)
        total_received = sum(tx.amount for tx in acc.received_transactions)

        transaction_risk_total = sum(
            tx.risk_score for tx in acc.sent_transactions + acc.received_transactions
        )

        mid_tx_count = 0
        small_tx_count = 0

        for tx in acc. sent_transactions + acc.received_transactions:
            if 5000 <= tx.amount <= 9999.9:
                mid_tx_count += 1

            if tx.amount < 3000:
                small_tx_count += 1

            if mid_tx_count >= 3:
                score += 3

            if mid_tx_count >= 6:
                score += 5

            if small_tx_count >= 10:
                score += 2

            if total_sent > 10000:
                score += 2

            elif total_received > 10000:
                score += 2

            if len(acc.connected_accounts) >= 3:
                score += 3

            if len(acc.connected_accounts) >= 5:
                score += 5

            if acc.hop_count >= 1:
                score += 5

            if acc.hop_count >= 3:
                score += 5

            if acc.max_hop_depth >= 3:
                score += 5

            if acc.max_hop_depth >= 4:
                score += 8

            if acc.max_hop_depth >= 5:
                score += 12

            if acc.multi_hop_count >= 5:
                score += 5

            if acc.multi_hop_count >= 10:
                score += 8

            if len(acc.sent_transactions) > 2 and len(acc.received_transactions) > 2:
                score +10
                acc.reasons.append("sent and received more than 2 transactions")

            if len(acc.sent_transactions) > 3 and len(acc.received_transactions) > 3:
                score +10
                acc.reasons.append("3+ sent and 3+ received more than 2 transactions")

            score += transaction_risk_total

            latitudes = []
            longitudes = []

            all_account_transactions = acc.sent_transactions + acc.received_transactions

            for tx in all_account_transactions:
                latitudes.append(tx.latitude)
                longitudes.append(tx.longitude)

            if len(latitudes) > 0:
                acc.avg_latitude = round(sum(latitudes) / len(latitudes), 6)
                acc.avg_longitude = round(sum(longitudes) / len(longitudes), 6)
            else:
                acc.avg_latitude = 0
                acc.avg_longitude = 0

            all_account_transactions = acc.sent_transactions + acc.received_transactions

            for tx in all_account_transactions:
                acc.merchants.add(tx.merchant_name)
                acc.locations.add(tx.location_address)
                acc.geo_distance_bands.add(tx.geo_distance_band)

                if tx.geo_risk_points > 0:
                    acc.risky_merchants.add(tx.merchant_name)

            acc.risk_score = score

def score_time_windows(accounts):
    all_transactions = []

    for acc in accounts.values():
        all_transactions.extend(acc.sent_transactions)

    all_tx = sorted(all_transactions, key=lambda tx: tx.date_obj)

    for i in range(len(all_tx)):
        start_date = all_tx[i].date_obj

        sent_7 = 0
        received_7 = 0
        sent_30 = 0
        received_30 = 0
        sent_60 = 0
        received_60 = 0
        sent_90 = 0
        received_90 = 0
        sent_120 = 0
        received_120 = 0

        for tx in all_tx:
            days = (tx.date_obj - start_date).days

            if 0 <= days <= 7:
                if tx.sender == acc.account_id:
                    sent_7 += tx.amount
                if tx.receiver == acc.account_id:
                    received_7 += tx.amount

                if 0 <= days <= 30:
                    if tx.sender == acc.account_id:
                        sent_30 += tx.amount
                    if tx.receiver == acc.account_id:
                        received_30 += tx.amount

                if 0 <= days <= 60:
                    if tx.sender == acc.account_id:
                        sent_60 += tx.amount
                    if tx.receiver == acc.account_id:
                        received_60 += tx.amount

                if 0 <= days <= 90:
                    if tx.sender == acc.account_id:
                        sent_90 += tx.amount
                    if tx.receiver == acc.account_id:
                        received_90 += tx.amount

                if 0 <= days <= 120:
                    if tx.sender == acc.account_id:
                        sent_120 += tx.amount
                    if tx.receiver == acc.account_id:
                        received_120 += tx.amount

                if sent_7 >= 10000 or received_7 >= 10000:
                    acc.risk_score += 5
                    acc.time_window_flag = 1

                if sent_30 >= 10000 or received_30 >= 10000:
                    acc.risk_score += 3
                    acc.time_window_flag = 1

                if sent_60 >= 15000 or received_60 >= 15000:
                    acc.risk_score += 3
                    acc.time_window_flag = 1

                if sent_90 >= 30000 or received_90 >= 30000:
                    acc.risk_score += 4
                    acc.time_window_flag = 1

                if sent_7 >= 50000 or received_7 >= 50000:
                    acc.risk_score += 5
                    acc.time_window_flag = 1

                if acc.time_window_flag == 1:
                    acc.reasons.append("timewindow activity detected")

def export_accounts(accounts):
    with open("accounts_output.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "account_id",
            "risk_score"
            "sent_count",
            "received_count",
            "connections",
            "max_hop_depth",
            "multi_hop_count",
            "time_window_flag",
            "avg_latitude",
            "avg_longitude",
            "two_way_activity_flag",
            "merchants",
            "risky_merchants",
            "locations",
            "geo_distance_bands"

        ])

        for acc in accounts.values():
            writer.writerow([
                acc.account_id,
                acc.risk_score,
                len(acc.sent_transactions),
                len(acc.received_transactions),
                len(acc.connected_accounts),
                acc.hop_count,
                acc.max_hop_depth,
                acc.multi_hop_count,
                acc.time_window_flag,
                acc.avg_latitude,
                acc.avg_longitude,
                acc.two_way_activity_flag,
                "; ".join(acc.merchants),
                "; ".join(acc.risky_merchants),
                "; ".join(acc.locations),
                "; ".join(acc.geo_distance_bands)
            ])

def export_suspicious_accounts(accounts):
    sorted_accounts = sorted(
        accounts.values(),
        key=lambda acc: acc.risk_score,
        reverse=True
    )

    with open("suspicious_accounts.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "account_id",
            "risk_score"
            "sent_count",
            "received_count",
            "connections",
            "max_hop_depth",
            "multi_hop_count",
            "time_window_flag",
            "avg_latitude",
            "avg_longitude"
        ])

        for acc in accounts.values():
            writer.writerow([
                acc.account_id,
                acc.risk_score,
                len(acc.sent_transactions),
                len(acc.received_transactions),
                len(acc.connected_accounts),
                acc.hop_count,
                acc.max_hop_depth,
                acc.multi_hop_count,
                acc.time_window_flag,
                acc.avg_latitude,
                acc.avg_longitude
            ])

transactions = load_transactions("transactions.csv")
accounts = build_accounts(transactions)

score_transactions(transactions)
count_hops(accounts)
calculate_hop_depth(accounts)
score_accounts(accounts)
score_time_windows(accounts)

export_accounts(accounts)
export_suspicious_accounts(accounts)

print("Analyzer complete.")
print("Files created.")
print("- accounts_output.csv.")
print("- suspicous_accounts.csv")
