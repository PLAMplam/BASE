import requests
import json
from datetime import datetime

BASE_BLOCKSCOUT_URL = "https://base.blockscout.com/api"

def analyze_wallet(address):
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc"
    }
    try:
        response = requests.get(BASE_BLOCKSCOUT_URL, params=params, timeout=10)
        data = response.json()
        if data.get('status') != '1' or not data.get('result'):
            return {"address": address, "error": "No transactions or API limit"}

        txs = data['result']
        contracts = set(t['to'].lower() for t in txs if t.get('to'))
        active_months = set(datetime.fromtimestamp(int(t['timeStamp'])).strftime('%Y-%m') for t in txs)
        gas_paid_eth = sum(int(t['gasUsed']) * int(t['gasPrice']) for t in txs) / 10**18

        score = 0
        if len(txs) >= 10: score += 20
        if len(txs) >= 50: score += 20
        if len(contracts) >= 5: score += 20
        if len(active_months) >= 3: score += 20
        if gas_paid_eth >= 0.005: score += 20

        return {
            "address": address,
            "total_tx": len(txs),
            "unique_contracts": len(contracts),
            "active_months": len(active_months),
            "gas_paid_eth": round(gas_paid_eth, 5),
            "score": score
        }
    except Exception as e:
        return {"address": address, "error": str(e)}

if __name__ == "__main__":
    try:
        with open("wallets.json", "r") as f:
            wallets = json.load(f)
    except FileNotFoundError:
        wallets = []

    results = [analyze_wallet(addr) for addr in wallets]

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Updated results.json successfully")
