
def hex_bytes(b: bytes) -> str:
    return " ".join('{:02x}'.format(x) for x in b)
