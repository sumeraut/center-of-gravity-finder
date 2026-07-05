import csv

def load_accounts_output(filename):
    accounts = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            account_id = row["account_id"]

            accounts[account_id] = {
                "account_id": account_id,
                "risk_score": float(row.get("risk_score", 0)),
                "sent_count": int(row.get("sent_count", 0)),
                "received_count": int(row.get("received_count", 0)),
                "connections": int(row.get("connections", 0)),
                "hop_count": int(row.get("hop_count", 0)),
                "max_hop_depth": int(row.get("max_hop_depth", 0)),
                "multi_hop_count": int(row.get("multi_hop_count", 0)),
                "time_window_flag": int(row.get("time_window_flag", 0)),
                "avg_latitude": float(row.get("avg_latitude", 0)),
                "avg_longitude": float(row.get("avg_longitude", 0)),
                "merchants": row.get("merchants", ""),
                "locations": row.get("locations", ""),
                "geo_distance_bands": row.get("geo_distance_bands", ""),
                "reasons": row.get("reasons", ""),
                "geo_match_count": 0,
                "geo_under_500_count": 0,
                "geo_501_1000_count": 0,
                "geo_1001_1599_count": 0,
                "geo_1600_1800_count": 0,
                "two_way_activity_flag": 0,
                "geo_proximity_score": 0.0,
                "risky_merchants": row.get("risky_merchants", ""),
                "matched_locations": "",
                "cog_score": 0.0,
                "cog_reasons": []
            }

    return accounts

def load_geo_accounts(filename, accounts):
    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            account_id = row["account_id"]

            if account_id in accounts:
                accounts[account_id]["geo_match_count"] = int(row.get("geo_match_count", 0))
                accounts[account_id]["geo_under_500_count"] = int(row.get("geo_under_500_count", 0))
                accounts[account_id]["geo_between_501_1000_count"] = int(row.get("geo_between_501_1000_count", 0))
                accounts[account_id]["geo_between_1001_1599_count"] = int(row.get("geo_between_1001_1599_count", 0))
                accounts[account_id]["geo_between_1600_1800_count"] = int(row.get("geo_between_1600_1800_count", 0))
                accounts[account_id]["geo_proximity_score"] = float(row.get("geo_proximity_score", 0))
                accounts[account_id]["matched_locations"] = row.get("matched_locations", "")

def calculate_cog_score(accounts):
    for acc in accounts.values():
        score = 0.0

        score += acc["risk_score"]

        if acc["risk_score"] > 0:
            acc["cog_reasons"].append("base analyzer risk included")

        if acc["hop_count"] >= 1:
            score += 5
            acc["cog_reasons"].append("account acts like hop/intermediary")

        if acc["hop_count"] >= 3:
            score += 5
            acc["cog_reasons"].append("repeated hopping behavior")

        if acc["max_hop_depth"] >= 3:
            score += 5
            acc["cog_reasons"].append("appears in 3-hop chain")

        if acc["max_hop_depth"] >= 4:
            score += 8
            acc["cog_reasons"].append("appears in 4-hop chain")

        if acc["max_hop_depth"] >= 5:
            score += 12
            acc["cog_reasons"].append("appears in 5-hop chain")

        if acc["connections"] >= 3:
            score += 3
            acc["cog_reasons"].append("connected to 3+ accounts")

        if acc["connections"] >= 5:
            score += 5
            acc["cog_reasons"].append("connected to 5+ accounts")

        if acc["time_window_flag"] == 1:
            score += 8
            acc["cog_reasons"].append("flagged time-window analysis")

        if acc["avg_latitude"] != 0 and acc["avg_longitude"] != 0:
             score += 5
             acc["cog_reasons"].append("account has  geographic coordinate activity")

        if acc["geo_proximity_score"] > 0:
            score += acc["geo_proximity_score"]

            acc["cog_reasons"].append(
                "geographic proximity to flagged corridor"
            )

        if acc["risky_merchants"] != "":
            score += 10

            acc["cog_reasons"].append(
                "connected to risky merchants"
            )

        if "under_500m" in acc["geo_distance_bands"]:
            score += 10
            acc["cog_reasons"].append("activity under 500 meters from reference location")

        if "between_501_1000m" in acc["geo_distance_bands"]:
            score += 7
            acc["cog_reasons"].append("activity between 501 and 1000 meters from reference location")

        if "between_1001_1599m" in acc["geo_distance_bands"]:
            score += 3
            acc["cog_reasons"].append("activity between 1001 and 1599 meters from reference location")

        if "between_1600_1800m" in acc["geo_distance_bands"]:
            score += 2
            acc["cog_reasons"].append("activity between 1600 and 1800 meters from reference location")

        if acc["two_way_activity_flag"] == 1:
            score += 6

            acc["cog_reasons"].append(
                "two-way sender/receiver behavior"
            )

        if acc["geo_match_count"] >= 1 and acc["hop_count"] >= 1:
            score += 10
            acc["cog_reasons"].append("geo match plus hopping behavior")

        if acc["geo_match_count"] >= 1 and acc ["max_hop_depth"] >= 4:
            score += 15
            acc["cog_reasons"].append("geo match plus deep multi-hop chain")

        acc["cog_score"] = score

def export_cog_groups(accounts):
    sorted_accounts = sorted(
        accounts.values(),
        key=lambda x: x["cog_score"],
        reverse=True
    )

    top_20 = sorted_accounts[:20]

    midpoint = len(sorted_accounts) // 2
    middle_20 = sorted_accounts[midpoint - 10: midpoint + 10]

    least_20 = sorted_accounts[-20:]

    write_group("top_20_cog_accounts.csv", top_20)
    write_group("middle_20_cog_accounts.csv", middle_20)
    write_group("least_20_cog_accounts.csv", least_20)

def write_group(filename, group):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "account_id",
            "cog_score",
            "risk_score",
            "hop_count",
            "max_hop_depth",
            "multi_hop_count",
            "connections",
            "time_window_flag",
            "geo_match_count",
            "geo_under_500_count",
            "geo_between_501_1000_count",
            "geo_between_1001_1599_count",
            "geo_between_1600_1800_count",
            "geo_proximity_score",
            "avg_latitude",
            "avg_longitude",
            "merchants",
            "risky_merchants",
            "locations",
            "geo_distance_bands",
            "matched_locations",
            "analyzer_reasons",
            "cog_reasons"
        ])

        for acc in group:
            writer.writerow([
                acc["account_id"],
                acc["cog_score"],
                acc["risk_score"],
                acc["hop_count"],
                acc["max_hop_depth"],
                acc["multi_hop_count"],
                acc["connections"],
                acc["time_window_flag"],
                acc["geo_match_count"],
                acc["geo_under_500_count"],
                acc["geo_between_501_1000_count"],
                acc["geo_between_1001_1599_count"],
                acc["geo_between_1600_1800_count"],
                acc["geo_proximity_score"],
                acc["avg_latitude"],
                acc["avg_longitude"],
                acc["merchants"],
                acc["risky_merchants"],
                acc["locations"],
                acc["geo_distance_bands"],
                acc["matched_locations"],
                acc["reasons"],
                "; ".join(acc["cog_reasons"])
            ])


def main():
    accounts = load_accounts_output("accounts_output.csv")
    load_geo_accounts("geo_risk_accounts.csv", accounts)

    calculate_cog_score(accounts)
    export_cog_groups(accounts)

    print("COG engine complete.")
    print("Files created:")
    print("- top_20_cog_accounts.csv")
    print("- middle_20_cog_accounts.csv")
    print("- least_20_cog_accounts.csv")

main()






