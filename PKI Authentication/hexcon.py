from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import binascii

with open("device_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

private_bytes = private_key.private_numbers().private_value.to_bytes(32, byteorder='big')

hex_array = ", ".join(f"0x{b:02X}" for b in private_bytes)
print(f"uint8_t privateKey[32] = {{ {hex_array} }};")
