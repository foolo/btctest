import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()



R_ARCHIVE_FILE = 'r_archive.txt'

def run2():
	with open(R_ARCHIVE_FILE, 'r') as archive_file:
		for line in archive_file:
			parts = line.strip().split('\t')
			if len(parts) != 4:
				raise ValueError(f'len(parts) != 4: {parts}')
			r_value_hex = parts[0]
			block_id = int(parts[1])
			tx_index = int(parts[2])
			input_index = int(parts[3])

			block_id_int = int(block_id)
			if block_id_int >= 22993:
				print(f'max reached, block_id_int: {block_id_int}')
				break

			print(f'r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
			cursor.execute("INSERT INTO numbers VALUES (?, ?, ?, ?)", (r_value_hex, block_id, tx_index, input_index))
		conn.commit()



if __name__ == '__main__':
	run2()
