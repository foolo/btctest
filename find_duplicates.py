import argparse
import sys


def find_duplicates():
	parser = argparse.ArgumentParser()
	parser.add_argument('archive_file_sorted', type=str)
	args = parser.parse_args()
	r_archive_file_sorted = args.archive_file_sorted

	line_count = 0
	with open(r_archive_file_sorted, 'r') as archive_file:
		current_r_value_hex = ""
		r_value_stack: list[str] = []
		for line in archive_file:
			line = line.strip()
			parts = line.split('\t')
			if len(parts) != 4:
				raise ValueError(f'len(parts) != 4: {parts}')
			r_value_hex = parts[0]
			if r_value_hex != current_r_value_hex:
				if len(r_value_stack) > 1:
					for r_value in r_value_stack:
						print(r_value)
				r_value_stack.clear()
			r_value_stack.append(line)
			current_r_value_hex = r_value_hex
			line_count += 1
	print(f'parsed {line_count} lines', file=sys.stderr)


if __name__ == '__main__':
	find_duplicates()
