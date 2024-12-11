import json
import struct
import hashlib

from sha256 import generate_hash

#SHA256_IMPL = "hashlib"
SHA256_IMPL = "custom"


def sha256_hash(data: bytes):
    if SHA256_IMPL == "hashlib":
        return hashlib.sha256(data).digest()
    if SHA256_IMPL == "custom":
        byte_arr = bytearray(data)
        return generate_hash(byte_arr)
    raise ValueError("Unknown SHA-256 implementation")
        


def fecth_content(url: str):
    import requests
    response = requests.get(url)
    #return response.content
    str = response.text
    return str


def bytes_to_target(bits: int):
    """Convert compact 'bits' field to target."""
    exponent = bits >> 24
    mantissa = bits & 0xFFFFFF
    target = mantissa * (2**(8 * (exponent - 3)))
    return target


def verify_nonce(block_header: bytes, bits: int):
    """Verify that the nonce in the block header meets the target."""
    # Double SHA-256 hash of the block header
    #hash1 = hashlib.sha256(block_header).digest()
    #hash2 = hashlib.sha256(hash1).digest()
    hash1 = sha256_hash(block_header)
    hash2 = sha256_hash(hash1)

    # Convert hash to a large integer (little-endian)
    hash_int = int.from_bytes(hash2, byteorder='little')

    # Calculate the target
    target = bytes_to_target(bits)

    # Verify if the hash is less than or equal to the target
    return hash_int <= target, hash_int, target


def main():
    print("Hello World!")

    block_height = 100
    #block_hash = "00000000b69bd8e4dc60580117617a466d5c76ada85fb7b87e9baea01f9d9984"
    json_url = f"https://blockchain.info/block-height/{block_height}"
    json_content = fecth_content(json_url)
    json_obj = json.loads(json_content)
    block_hash_onchain = json_obj["blocks"][0]["hash"]
    print('block_hash_onchain hash', block_hash_onchain)
    raw_url = f"https://blockchain.info/rawblock/{block_hash_onchain}?format=hex"
    block_data_hex = fecth_content(raw_url)
    block_data_bin = bytes.fromhex(block_data_hex)

    block_header = block_data_bin[:80]

    # Extract 'bits' (bytes 72-76) as little-endian integer
    bits: int = struct.unpack("<I", block_header[72:76])[0]
    print(f"Bits: {bits}", "typeof bits: ", type(bits))

    # Verify nonce
    is_valid, block_hash_int, target = verify_nonce(block_header, bits)
    block_hash_recreated = block_hash_int.to_bytes(32, byteorder='big').hex()
    print(f"Nonce Valid: {is_valid}")
    print(f"Block Hash: {block_hash_int}")
    print(f"Block Hash Hex: {block_hash_recreated}")
    print(f"Target: {target}")
    if block_hash_recreated == block_hash_onchain:
        print("Block hash matches!")
    else:
        print("Block hash does not match!")

if __name__ == "__main__":
    main()
