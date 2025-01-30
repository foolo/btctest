import argparse


def find_duplicates():
	parser = argparse.ArgumentParser()
	parser.add_argument('archive_file_sorted', type=str)
	args = parser.parse_args()
	r_archive_file_sorted = args.archive_file_sorted

	line_count = 0
	with open(r_archive_file_sorted, 'r') as archive_file:
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
			line_count += 1
	print(f'parsed {line_count} lines')


if __name__ == '__main__':
	find_duplicates()
