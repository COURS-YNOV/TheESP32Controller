def make_command(test_name: str) -> bytes:
    return f"RUN_{test_name.upper()}".encode('utf-8')
