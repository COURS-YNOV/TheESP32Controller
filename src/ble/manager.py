from bleak import BleakScanner

async def scan_ble_devices():
    print("⏳ Scanning...")
    devices = await BleakScanner.discover(timeout=5.0)
    
    found_devices = []
    one_device_found = False
        
    for device in devices:
        if device.name and device.name.startswith("ESP32"):
            print(f"📡 Found: {device.name} - {device.address}")
            one_device_found = True
            found_devices.append(device)
    
    if one_device_found:
        print("⏳ Scan complete. New devices listed.\n")
    else:
        print("❌ No devices found.\n")
        
    return found_devices
