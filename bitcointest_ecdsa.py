import json
#from bitcoinlib.services.services import Service
import sqlite3
import sys
from typing import TextIO
from bitcoinlib.scripts import Script

conn = sqlite3.connect("work/example.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS numbers (
  r_value_hex TEXT NOT NULL,
  block_number INTEGER NOT NULL,
  tx_index INTEGER NOT NULL,
  input_index INTEGER NOT NULL,
  PRIMARY KEY (r_value_hex)			 -- Ensures logarithmic insertion on `num`
)
""")


def fetch_content(url: str):
	import requests
	response = requests.get(url)
	#return response.content
	str = response.text
	return str


# Specify the block height
# start_block = 223302
# block_count = 1


def get_r_value(sig: str) -> int:
	script = Script.parse(sig)
	signatures = script.signatures
	if len(signatures) != 1:
		raise ValueError(f'len(signatures) != 1: {signatures}')
	signature = signatures[0]
	return signature.r

def handle_block(block_id: int, errlog_file: TextIO) -> list[str]:
		print(f'\rblock_id: {block_id}', end='\t', flush=True)
		json_url = f"https://blockchain.info/block-height/{block_id}"
		json_content = fetch_content(json_url)
		json_obj = json.loads(json_content)
		num_blocks = len(json_obj["blocks"])
		if num_blocks != 1:
			errmsg = f'num_blocks is not 1: {num_blocks} for block {block_id}'
			errlog_file.write(f'{errmsg}\n')
			print(f'ERROR: {errmsg}')
			sys.exit(1)
		transactions = json_obj["blocks"][0]["tx"]
		new_lines: list[str] = []
		#print(f'num_transactions: {len(transactions)}')
		for tx_index, tx in enumerate(transactions):
			if tx_index == 0:
				continue # skip coinbase transaction
			inputs = tx["inputs"]
			for input_index, input in enumerate(inputs):
				signatures = input["script"]
				try:
					r_value = get_r_value(signatures)
				except Exception as e:
					error_msg = f'block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}, {e}'
					print(f'ERROR: {error_msg}')
					errlog_file.write(f'{error_msg}\n')
					errlog_file.flush()
					continue
				r_value_hex = hex(r_value)[2:]

				# fake r_value_hex
				#r_value_hex = r_value_hex[0:5]

				print(f'r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
				try:
					with conn:
						print(f'INSERT INTO numbers VALUES ({r_value_hex}, {block_id}, {tx_index}, {input_index})')
						cursor.execute("INSERT INTO numbers VALUES (?, ?, ?, ?)", (r_value_hex, block_id, tx_index, input_index))
				except sqlite3.IntegrityError:
					errlog_file.write(f'IntegrityError: {r_value_hex}\t{block_id}\t{tx_index}\t{input_index}\n')
					errlog_file.flush()
					continue

				new_lines.append(f'{r_value_hex}\t{block_id}\t{tx_index}\t{input_index}\n')
		return new_lines


NEXT_BLOCK_FILE = 'work/next_block.txt'
R_ARCHIVE_FILE = 'work/r_archive.txt'

def run2():

	try:
		with open(NEXT_BLOCK_FILE, 'r') as next_block_file:
			next_block = int(next_block_file.read())
			print(f'next_block: {next_block}')
	except FileNotFoundError:
		next_block = 223300
	
	

	# open a text file for err logs
	with open('work/err_log.txt', 'w') as errlog_file:
		with open(R_ARCHIVE_FILE, 'a') as archive_file:
			while True:
				new_lines = handle_block(next_block, errlog_file)
				errlog_file.flush()
				archive_file.writelines(new_lines)
				archive_file.flush()
				next_block += 1
				with open(NEXT_BLOCK_FILE, 'w') as next_block_file:
					next_block_file.write(str(next_block))


def run():

	# Initialize a Bitcoinlib Service (using default Bitcoin node or public APIs)
	service = Service()

	for block_id in range(start_block, start_block + block_count):
		block = service.getblock(block_id)
		if not block:
			raise ValueError(f'block {block_id} not found')
		print(f'block: {block}')
		txns = block.transactions
		if txns is None:
			print(f'WARNING: txns is None for block {block_id}')
			continue
		#signatures: list[tuple[int, int, int, int]] = []
		for txn_index, txn in enumerate(txns[1:]):
			print(f'txn: {txn}')
			for input_index, input in enumerate(txn.inputs):
				print(f'input: {input}')
				sigs = input.script.signatures
				for sig in sigs:
					print(f'sig: {repr(sig)}')
					r_value = hex(sig.r)[2:]
					signature = (r_value, block_id, txn_index, input_index)
					#signatures.append(signature)
					cursor.execute("INSERT INTO numbers VALUES (?, ?, ?, ?)", signature)

		#cursor.executemany("INSERT INTO numbers VALUES (?, ?, ?, ?)", signatures)


if __name__ == '__main__':
	run2()
