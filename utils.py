from bitcoinlib.scripts import Script


def get_r_values_from_script(script: str) -> list[int]:
	script = Script.parse(script)
	signatures = script.signatures
	r_values = [signature.r for signature in signatures]
	return r_values


def fetch_content(url: str):
	import requests
	response = requests.get(url)
	str = response.text
	return str
