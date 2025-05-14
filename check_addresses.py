import argparse
import json
import sys
from tqdm import tqdm

from utils import fetch_content


def get_btc_address_for_tx_hash(tx_hash: str) -> str | None:
	json_url = f"https://blockchain.info/rawtx/{tx_hash}"
	json_content = fetch_content(json_url)
	json_obj = json.loads(json_content)
	inputs = json_obj["inputs"]
	if len(inputs) < 1:
		raise ValueError(f'len(inputs) < 1')
	address0 = inputs[0]["prev_out"]["addr"]
	for i in range(1, len(inputs)):
		addr = inputs[i]["prev_out"]["addr"]
		if addr != address0:
			print(f'WARNING: multiple addresses found for tx_hash {tx_hash}: {address0} and {addr}', file=sys.stderr)
			return None
	return address0


def get_all_balances(addresses: list[str]) -> dict[str, int]:
	balances: dict[str, int] = {}
	json_url = f"https://blockchain.info/balance?active={'|'.join(addresses)}"
	json_content = fetch_content(json_url)
	json_obj = json.loads(json_content)
	for address in addresses:
		if address not in json_obj:
			raise ValueError(f'WARNING: address {address} not found')
		balance = json_obj[address]["final_balance"]
		balances[address] = balance
	return balances


def check_addresses():
	parser = argparse.ArgumentParser()
	parser.add_argument('keys_and_transactions', type=str)
	args = parser.parse_args()
	assert isinstance(args.keys_and_transactions, str)

	with open(args.keys_and_transactions, 'r') as f:
		lines = f.readlines()

		all_addresses: set[str] = set()

		for line in tqdm(lines):
			line = line.strip()
			parts = line.split('\t')
			#private_key = int(parts[0])
			tx_hash1 = parts[1]
			tx_hash2 = parts[2]

			address1 = get_btc_address_for_tx_hash(tx_hash1)
			address2 = get_btc_address_for_tx_hash(tx_hash2)
			if address1 and not address1 in all_addresses:
				all_addresses.add(address1)
			if address2 and not address2 in all_addresses:
				all_addresses.add(address2)

		all_addresses_list = list(all_addresses)
		balances = get_all_balances(all_addresses_list)
		for address, balance in balances.items():
			print(f'address {address}, balance: {balance}', file=sys.stderr)


if __name__ == '__main__':
	check_addresses()
