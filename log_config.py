import logging
import sys


def initialize_logger(log_file: str) -> logging.Logger:
	logger = logging.Logger('app')
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	handler = logging.FileHandler(log_file)
	handler.setFormatter(formatter)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)
	stream_handler = logging.StreamHandler(sys.stdout)
	stream_handler.setFormatter(formatter)
	logger.addHandler(stream_handler)
	return logger
