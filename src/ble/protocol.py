def make_command(test_name: str) -> bytes:
    return f"RUN_{test_name.upper()}_TEST".encode('utf-8')
