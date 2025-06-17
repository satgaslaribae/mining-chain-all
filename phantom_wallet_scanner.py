"""
Phantom Wallet Scanner — инструмент для поиска "фантомных" или неотображаемых токенов в Ethereum-кошельке.

Некоторые токены могут быть отправлены на адрес, но не отображаются в популярных интерфейсах (например, Metamask),
из-за отсутствия метаданных, поддержки, или фильтрации UI. Этот скрипт находит такие токены через историю взаимодействий.
"""

import requests
import argparse


ETHERSCAN_API_URL = "https://api.etherscan.io/api"


def get_erc20_tokens(address, api_key):
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key,
    }
    response = requests.get(ETHERSCAN_API_URL, params=params)
    result = response.json()
    return result.get("result", [])


def find_phantom_tokens(events):
    tokens = {}
    for tx in events:
        contract = tx["contractAddress"]
        symbol = tx.get("tokenSymbol", "")
        name = tx.get("tokenName", "")
        if contract not in tokens:
            tokens[contract] = {
                "symbol": symbol,
                "name": name,
                "received": 0,
                "sent": 0
            }

        if tx["to"].lower() == address.lower():
            tokens[contract]["received"] += int(tx["value"])
        elif tx["from"].lower() == address.lower():
            tokens[contract]["sent"] += int(tx["value"])

    phantom = []
    for contract, data in tokens.items():
        net_balance = data["received"] - data["sent"]
        if net_balance > 0 and (data["symbol"] == "" or data["name"] == ""):
            phantom.append({
                "contract": contract,
                "balance": net_balance,
                "name": data["name"] or "UNKNOWN",
                "symbol": data["symbol"] or "UNKNOWN"
            })
    return phantom


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phantom Wallet Scanner — поиск невидимых токенов")
    parser.add_argument("address", help="Ethereum-адрес")
    parser.add_argument("api_key", help="API-ключ от Etherscan")
    args = parser.parse_args()

    address = args.address
    api_key = args.api_key

    print(f"[•] Сканируем {address} на предмет фантомных токенов...")
    events = get_erc20_tokens(address, api_key)

    phantom_tokens = find_phantom_tokens(events)

    print("\n[!] Найдены фантомные токены:")
    if not phantom_tokens:
        print("  — Нет фантомных токенов.")
    else:
        for token in phantom_tokens:
            print(f"  - Контракт: {token['contract']} | Символ: {token['symbol']} | Баланс: {token['balance']}")
