import subprocess

R_ARCHIVE_FILE = 'work/r_archive.txt'
TMP_FILE = '/tmp/r_archive_tmp.txt'
R_ARCHIVE_FILE_SORTED = '/tmp/r_archive_sorted.txt'


def find_duplicates():

	subprocess.run(['cp', R_ARCHIVE_FILE, TMP_FILE])
	subprocess.run(['sort', '--output', R_ARCHIVE_FILE_SORTED, TMP_FILE])

	line_count = 0
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
			line_count += 1
	print(f'parsed {line_count} lines')


if __name__ == '__main__':
	find_duplicates()
