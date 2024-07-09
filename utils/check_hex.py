import re

def is_hex_string(s):
    if s.startswith("0x"):
        s = s[2:]
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    return bool(hex_pattern.match(s))