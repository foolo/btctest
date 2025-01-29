import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()



R_ARCHIVE_FILE_SORTED = 'r_archive_sorted.txt'

def find_duplicates():
	with open(R_ARCHIVE_FILE_SORTED, 'r') as archive_file:
		previous_r_value_hex = ""
		for line in archive_file:
			parts = line.strip().split('\t')
			if len(parts) != 4:
				raise ValueError(f'len(parts) != 4: {parts}')
			r_value_hex = parts[0]
			block_id = int(parts[1])
			tx_index = int(parts[2])
			input_index = int(parts[3])
			if r_value_hex == previous_r_value_hex:
				print(f'duplicate r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
			previous_r_value_hex = r_value_hex

			#print(f'r_value_hex: {r_value_hex}, block_id: {block_id}, tx_index: {tx_index}, input_index: {input_index}')
		conn.commit()



if __name__ == '__main__':
	find_duplicates()
