import re


ROKKA_NAME_PATTERN = re.compile(r'^[0-9a-f]{40}\.[a-zA-Z]{2,4}$')

def is_rokka_name(name: str):
    return bool(ROKKA_NAME_PATTERN.match(name))