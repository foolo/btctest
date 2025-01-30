import argparse
import json
#from bitcoinlib.services.services import Service
import logging
import os
import sqlite3
import sys
from typing import TextIO
from bitcoinlib.scripts import Script
import subprocess

from log_config import initialize_logger

## pip install bitcoinlib


def get_r_value(sig: str) -> int:
	script = Script.parse(sig)
	signatures = script.signatures
	if len(signatures) != 1:
		raise ValueError(f'len(signatures) != 1: {signatures}')
	signature = signatures[0]
	return signature.r


def runCommandAndGetOutput(command: list[str]) -> str:
	print(f'command: {command}')
	output = subprocess.run(command, capture_output=True, text=True)
	if output.returncode != 0:
		raise Exception(f'Error running command: {command}, output: {output}')
	return output.stdout


def handle_block(block_id: int, logger: logging.Logger) -> list[str]:
	print(f'\rblock_id: {block_id}', end='\t', flush=True)
	block_hash = runCommandAndGetOutput(['bitcoin-cli', 'getblockhash', str(block_id)]).strip()
	block = runCommandAndGetOutput(['bitcoin-cli', 'getblock', block_hash])
	print(f'len block_obj: {len(block)}, type: {type(block)}')
	block_obj = json.loads(block)
	transactions = block_obj["tx"]
	new_lines: list[str] = []
	#print(f'num_transactions: {len(transactions)}')
	for tx_index, tx_hash in enumerate(transactions):
		if tx_index == 0:
			continue  # skip coinbase transaction
		raw_tx = runCommandAndGetOutput(['bitcoin-cli', 'getrawtransaction', tx_hash, '2', block_hash])
		tx = json.loads(raw_tx)
		inputs = tx["vin"]
		for input_index, input in enumerate(inputs):
			signatures = input["scriptSig"]["hex"]
			try:
				r_value = get_r_value(signatures)
			except Exception as e:
				error_msg = f'block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}, {e}'
				logger.error(f'{error_msg}\n')
				continue
			r_value_hex = hex(r_value)[2:]

			# fake r_value_hex
			#r_value_hex = r_value_hex[0:5]

			print(f'r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
			# try:
			# 	with conn:
			# 		print(f'INSERT INTO numbers VALUES ({r_value_hex}, {block_id}, {tx_index}, {input_index})')
			# 		cursor.execute("INSERT INTO numbers VALUES (?, ?, ?, ?)", (r_value_hex, block_id, tx_index, input_index))
			# except sqlite3.IntegrityError:
			# 	errlog_file.write(f'IntegrityError: {r_value_hex}\t{block_id}\t{tx_index}\t{input_index}\n')
			# 	errlog_file.flush()
			# 	continue

			new_lines.append(f'{r_value_hex}\t{block_id}\t{tx_index}\t{input_index}\n')
	return new_lines


def run2():
	parser = argparse.ArgumentParser()
	parser.add_argument('work_dir', help='work directory')
	args = parser.parse_args()
	work_dir = args.work_dir

	NODE_NEXT_BLOCK_FILE = os.path.join(work_dir, 'node_next_block.txt')
	NODE_R_ARCHIVE_FILE = os.path.join(work_dir, 'node_r_archive.txt')
	NODE_ERR_LOG_FILE = os.path.join(work_dir, 'node_err_log.txt')

	logger = initialize_logger(NODE_ERR_LOG_FILE)
	logger.info('app started')

	try:
		with open(NODE_NEXT_BLOCK_FILE, 'r') as next_block_file:
			next_block = int(next_block_file.read())
			print(f'next_block: {next_block}')
	except FileNotFoundError:
		next_block = 0

	with open(NODE_R_ARCHIVE_FILE, 'a') as archive_file:
		while True:
			new_lines = handle_block(next_block, logger)
			archive_file.writelines(new_lines)
			archive_file.flush()
			next_block += 1
			with open(NODE_NEXT_BLOCK_FILE, 'w') as next_block_file:
				next_block_file.write(str(next_block))


if __name__ == '__main__':
	run2()
