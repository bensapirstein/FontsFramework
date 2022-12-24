
import subprocess

def parse_list(string: str) -> list:
    """Convert a string representation of a list to a list."""
    return [s.strip("''") for s in string.strip('[]').split(', ')]

def normalize_ufo(path_to_ufo):
    subprocess.run(['psfnormalize', path_to_ufo.replace(' ', '\ ')])
