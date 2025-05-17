import argparse
import sys
from tqdm import tqdm
from dataclasses import dataclass
from sympy import mod_inverse


@dataclass
class SignatureInfo:
	r: int
	s: int
	signature_hash_int: int
	tx_hash: str
	input_index: int


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
	print(f"Recovered private key: {private_key}, txn hash: {sig_info1.tx_hash}, {sig_info2.tx_hash}", file=sys.stderr)
	print(f"{private_key}\t{sig_info1.tx_hash}\t{sig_info1.input_index}\t{sig_info2.tx_hash}\t{sig_info2.input_index}")


def solve_pairs():
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
			if len(parts) != 5:
				raise ValueError(f'len(parts) != 5: {parts}')
			r_int = int(parts[0])
			s_int = int(parts[1])
			signature_hash_int = int(parts[2])
			tx_hash = parts[3]
			input_index = int(parts[4])
			signature_info = SignatureInfo(r_int, s_int, signature_hash_int, tx_hash, input_index)
			if r_int not in r_to_signature_hash:
				r_to_signature_hash[r_int] = []
			r_to_signature_hash[r_int].append(signature_info)

		print(f'parsed {len(r_to_signature_hash)} lines', file=sys.stderr)

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
					solve_pair(sig_info_i, sig_info_j)


if __name__ == '__main__':
	solve_pairs()
