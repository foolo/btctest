import argparse
from dataclasses import dataclass
import json
import sys
from typing import Any
from bitcoinlib.scripts import Script
from bitcoinlib.transactions import Transaction


def fetch_content(url: str):
	import requests
	response = requests.get(url)
	str = response.text
	return str


def get_signature_and_tx_hash(block_id: int, tx_index: int, input_index: int) -> tuple[int, int, str]:
	json_url = f"https://blockchain.info/block-height/{block_id}"
	json_content = fetch_content(json_url)
	json_obj = json.loads(json_content)
	tx = json_obj["blocks"][0]["tx"][tx_index]
	tx_hash = tx["hash"]
	script = tx["inputs"][input_index]["script"]
	script = Script.parse(script)
	signatures = script.signatures
	if len(signatures) != 1:
		print(f'len(signatures) != 1: {len(signatures)}')
		sys.exit(1)
	return signatures[0].r, signatures[0].s, tx_hash


def get_signature_hash(tx_hash: str, input_index: int) -> str:
	tx_hex = fetch_content(f"https://blockchain.info/rawtx/{tx_hash}?format=hex")
	tx = Transaction.parse(tx_hex)
	input = tx.inputs[input_index]
	hash_type = input.hash_type
	signature_hash = tx.signature_hash(input_index, hash_type)
	return signature_hash.hex()


def parse_duplicates():
	parser = argparse.ArgumentParser()
	parser.add_argument('duplicates', type=str)
	args = parser.parse_args()
	duplicates = args.duplicates

	with open(duplicates, 'r') as archive_file:
		sign_infos: dict[str, dict[str, Any]] = {}
		for line in archive_file:
			line = line.strip()
			parts = line.split('\t')
			if len(parts) != 4:
				raise ValueError(f'len(parts) != 4: {parts}')
			r_value_hex = parts[0]
			block_id = int(parts[1])
			tx_index = int(parts[2])
			input_index = int(parts[3])
			r, s, tx_hash = get_signature_and_tx_hash(block_id, tx_index, input_index)
			r_ref_hex = hex(r)[2:]
			if r_ref_hex != r_value_hex:
				print(f'r != r_value_hex: {r_ref_hex} != {r_value_hex}')
				sys.exit(1)
			try:
				signature_hash = get_signature_hash(tx_hash, input_index)
			except Exception as e:
				print(f'error: {e}', file=sys.stderr)
				continue
			signature_hash_int = int(signature_hash, 16)
			sign_info: dict[str, Any] = {'signature_hash': signature_hash, 'r': r, 's': s}
			sign_infos[r_value_hex] = sign_info
			print(f'{r}\t{s}\t{signature_hash_int}\t{tx_hash}')


if __name__ == '__main__':
	parse_duplicates()
