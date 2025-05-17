import argparse
import json
import sys
from tqdm import tqdm
from dataclasses import dataclass
from sympy import mod_inverse

from utils import fetch_content


@dataclass
class SignatureInfo:
	r: int
	s: int
	signature_hash_int: int
	tx_hash: str
	input_index: int
	block_id: int
	tx_index: int


def solve_pair(sig_info1: SignatureInfo, sig_info2: SignatureInfo):
	r = sig_info1.r
	s1 = sig_info1.s
	s2 = sig_info2.s
	h1 = sig_info1.signature_hash_int
	h2 = sig_info2.signature_hash_int

	# Curve order for Secp256k1, https://en.bitcoin.it/wiki/Secp256k1
	n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

	k = ((h1 - h2) * mod_inverse(s1 - s2, n)) % n

	private_key = ((s1 * k - h1) * mod_inverse(r, n)) % n
	#print(f"Recovered private key: {private_key}, txn hash: {sig_info1.tx_hash}, {sig_info2.tx_hash}", file=sys.stderr)
	return private_key


def solve_pairs() -> dict[int, tuple[SignatureInfo, SignatureInfo]]:
	parser = argparse.ArgumentParser()
	parser.add_argument('value_sets', type=str)
	args = parser.parse_args()
	assert isinstance(args.value_sets, str)

	r_to_signature_hash: dict[int, list[SignatureInfo]] = {}

	with open(args.value_sets, 'r') as f:
		lines = f.readlines()
		line_count = len(lines)
		print(f'parsed {line_count} lines', file=sys.stderr)
		for line in tqdm(lines):
			line = line.strip()
			parts = line.split('\t')
			if len(parts) != 7:
				raise ValueError(f'len(parts) != 7: {parts}')
			r_int = int(parts[0])
			s_int = int(parts[1])
			signature_hash_int = int(parts[2])
			tx_hash = parts[3]
			input_index = int(parts[4])
			block_id = int(parts[5])
			tx_index = int(parts[6])
			signature_info = SignatureInfo(r_int, s_int, signature_hash_int, tx_hash, input_index, block_id, tx_index)
			if r_int not in r_to_signature_hash:
				r_to_signature_hash[r_int] = []
			r_to_signature_hash[r_int].append(signature_info)

		print(f'parsed {len(r_to_signature_hash)} lines', file=sys.stderr)

	results: dict[int, tuple[SignatureInfo, SignatureInfo]] = {}

	for r_int, signature_infos in r_to_signature_hash.items():
		if len(signature_infos) > 1:
			print(f'found {len(signature_infos)} signatures with r_int {r_int}', file=sys.stderr)
			for i in range(len(signature_infos)):
				for j in range(i + 1, len(signature_infos)):
					sig_info_i = signature_infos[i]
					sig_info_j = signature_infos[j]
					if sig_info_i.s == sig_info_j.s:
						print(f'skip same s: {sig_info_i.s}', file=sys.stderr)
						continue
					if sig_info_i.signature_hash_int == sig_info_j.signature_hash_int:
						print(f'skip same signature_hash_int: {sig_info_i.signature_hash_int}', file=sys.stderr)
						continue
					private_key = solve_pair(sig_info_i, sig_info_j)
					if private_key not in results:
						results[private_key] = (sig_info_i, sig_info_j)
	print(f'found {len(results)} pairs', file=sys.stderr)
	return results


def get_btc_address_for_tx_hash(tx_hash: str, input_index: int) -> str | None:
	json_url = f"https://blockchain.info/rawtx/{tx_hash}"
	json_content = fetch_content(json_url)
	json_obj = json.loads(json_content)
	inputs = json_obj["inputs"]
	if len(inputs) < 1:
		raise ValueError(f'len(inputs) < 1')
	return inputs[input_index]["prev_out"]["addr"]


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


from bitcoinlib.keys import Key


def private_key_to_address(private_key: int, compressed: bool) -> str:
	key = Key(import_key=private_key)
	return key.address(compressed=compressed)


def check_results(results: dict[int, tuple[SignatureInfo, SignatureInfo]]):
	all_addresses: dict[str, int] = {}

	for private_key, (sig_info_i, sig_info_j) in tqdm(results.items()):
		tx_hash1 = sig_info_i.tx_hash
		input_index1 = sig_info_i.input_index
		tx_hash2 = sig_info_j.tx_hash
		input_index2 = sig_info_j.input_index

		address1 = get_btc_address_for_tx_hash(tx_hash1, input_index1)
		address2 = get_btc_address_for_tx_hash(tx_hash2, input_index2)
		# print(f'private_key: {private_key}, tx_hash1: {tx_hash1}, input_index1: {input_index1}, address1: {address1}')
		# print(f'private_key: {private_key}, tx_hash2: {tx_hash2}, input_index2: {input_index2}, address2: {address2}')

		addr_ref_uncompressed = private_key_to_address(private_key, compressed=False)
		addr_ref_compressed = private_key_to_address(private_key, compressed=True)
		if address1 != addr_ref_uncompressed and address1 != addr_ref_compressed:
			print(f'WARNING: address1 != addr_ref: {address1} != {addr_ref_uncompressed} or {addr_ref_compressed}', file=sys.stderr)
			continue
		if address2 != addr_ref_uncompressed and address2 != addr_ref_compressed:
			print(f'WARNING: address2 != addr_ref: {address2} != {addr_ref_uncompressed} or {addr_ref_compressed}', file=sys.stderr)
			continue

		if address1 != address2:
			print(f'WARNING: address1 != address2: {address1} != {address2}', file=sys.stderr)

		if address1 and not address1 in all_addresses:
			all_addresses[address1] = private_key
		if address2 and not address2 in all_addresses:
			all_addresses[address2] = private_key

		if len(all_addresses) > 10:
			break

	for address, private_key in all_addresses.items():
		print(f'{address}\t{private_key}')


if __name__ == '__main__':
	solve_results = solve_pairs()
	check_results(solve_results)
