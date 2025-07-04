from ble.protocol import make_command

def test_make_command_led():
    result = make_command('led')
    assert result == b'RUN_LED'
