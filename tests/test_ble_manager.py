import pytest
from unittest.mock import AsyncMock, patch
from ble.manager import scan_ble_devices

@pytest.mark.asyncio
async def test_scan_ble_devices_returns_devices():
    fake_device = type('FakeBLE', (object,), {'name': 'ESP32', 'address': 'AA:BB:CC'})()
    
    with patch('ble.manager.BleakScanner.discover', new=AsyncMock(return_value=[fake_device])):
        devices = await scan_ble_devices()
        
        assert len(devices) == 1
        assert devices[0].name == 'ESP32'
        assert devices[0].address == 'AA:BB:CC'
