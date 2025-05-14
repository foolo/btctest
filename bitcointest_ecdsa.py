import argparse
import json
import logging
import os
import sys
from bitcoinlib.scripts import Script
from log_config import initialize_logger
from utils import get_r_values_from_script


def fetch_content(url: str):
	import requests
	response = requests.get(url)
	str = response.text
	return str


def handle_block(block_id: int, logger: logging.Logger) -> list[str]:
	print(f'\rblock_id: {block_id}', end='\t', flush=True)
	json_url = f"https://blockchain.info/block-height/{block_id}"
	json_content = fetch_content(json_url)
	json_obj = json.loads(json_content)
	num_blocks = len(json_obj["blocks"])
	if num_blocks != 1:
		errmsg = f'num_blocks is not 1: {num_blocks} for block {block_id}'
		logger.error(f'{errmsg}\n')
		print(f'ERROR: {errmsg}')
		sys.exit(1)
	transactions = json_obj["blocks"][0]["tx"]
	new_lines: list[str] = []
	#print(f'num_transactions: {len(transactions)}')
	for tx_index, tx in enumerate(transactions):
		if tx_index == 0:
			continue  # skip coinbase transaction
		inputs = tx["inputs"]
		for input_index, input in enumerate(inputs):
			signatures = input["script"]
			try:
				r_values = get_r_values_from_script(signatures)
				for r_value in r_values:
					r_value_hex = hex(r_value)[2:]
					print(f'r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
					new_lines.append(f'{r_value_hex}\t{block_id}\t{tx_index}\t{input_index}\n')
			except Exception as e:
				error_msg = f'block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}, {e}'
				logger.error(f'{error_msg}\n')
				continue
	return new_lines


def run2():

	parser = argparse.ArgumentParser()
	parser.add_argument('work_dir', help='work directory')
	args = parser.parse_args()
	assert isinstance(args.work_dir, str)

	NEXT_BLOCK_FILE = os.path.join(args.work_dir, 'next_block.txt')
	R_ARCHIVE_FILE = os.path.join(args.work_dir, 'r_archive.txt')
	ERR_LOG_FILE = os.path.join(args.work_dir, 'err_log.txt')

	logger = initialize_logger(ERR_LOG_FILE)
	logger.info('app started')

	try:
		with open(NEXT_BLOCK_FILE, 'r') as next_block_file:
			next_block = int(next_block_file.read())
			print(f'next_block: {next_block}')
	except FileNotFoundError:
		next_block = 0

	with open(R_ARCHIVE_FILE, 'a') as archive_file:
		while True:
			new_lines = handle_block(next_block, logger)
			archive_file.writelines(new_lines)
			archive_file.flush()
			next_block += 1
			with open(NEXT_BLOCK_FILE, 'w') as next_block_file:
				next_block_file.write(str(next_block))


if __name__ == '__main__':
	run2()
