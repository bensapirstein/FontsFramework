def parse_list(string: str) -> list:
    """Convert a string representation of a list to a list."""
    return [s.strip("''") for s in string.strip('[]').split(', ')]