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
    
    response = requests.get(BASE_BLOCKSCOUT_URL, params=params)
    data = response.json()
    
    if data.get('status') != '1' or not data.get('result'):
        return {"error": "Invalid address or no transactions found"}

    txs = data['result']
    total_tx = len(txs)
    
    contracts = set()
    active_months = set()
    total_gas_used = 0

    for tx in txs:
        if tx.get('to'):
            contracts.add(tx['to'].lower())
        
        tx_date = datetime.fromtimestamp(int(tx['timeStamp']))
        active_months.add(f"{tx_date.year}-{tx_date.month}")
        
        total_gas_used += int(tx['gasUsed']) * int(tx['gasPrice'])

    gas_paid_eth = total_gas_used / 10**18

    # Scoring Rules
    score = 0
    if total_tx >= 10: score += 20
    if total_tx >= 50: score += 20
    if len(contracts) >= 5: score += 20
    if len(active_months) >= 3: score += 20
    if gas_paid_eth >= 0.005: score += 20

    return {
        "address": address,
        "total_tx": total_tx,
        "unique_contracts": len(contracts),
        "active_months": len(active_months),
        "gas_paid_eth": round(gas_paid_eth, 5),
        "estimated_score": score
    }

if __name__ == "__main__":
    target_address = "0xfc0cbfbc5245fd333efba768ceeedb3ef66d602e"
    result = analyze_wallet(target_address)
    print(json.dumps(result, indent=2))
