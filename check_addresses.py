import argparse
import json
import sys
from typing import Any
from tqdm import tqdm

from utils import fetch_content


def get_balances(addresses: list[str]) -> dict[str, int]:
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

		addresses: list[tuple[str, int]] = []
		all_balances: dict[str, int] = {}
		for line in lines:
			print('------')
			line = line.strip()
			parts = line.split('\t')
			address = parts[0]
			private_key = int(parts[1])

		# todo, check balances


if __name__ == '__main__':
	check_addresses()
