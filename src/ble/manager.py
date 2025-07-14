from bleak import BleakScanner, BleakClient

class BLEManager:
    def __init__(self):
        self.client = None
        self.connected_device = None
        self.found_devices = []
        self.one_device_found = False
        self.write_char_uuid = "2A19"  # UUID writeCharacteristic
        self.notify_char_uuid = "2A20" # UUID notifyCharacteristic
        self.on_disconnect_callback = None

    async def scan_devices(self):
        print("⏳ Scanning for BLE devices...")
        self.found_devices.clear()
        devices = await BleakScanner.discover(timeout=5.0)
    
        for device in devices:
            if device.name and device.name.startswith("ESP32"):
                print(f"📡 Found: {device.name} - {device.address}")
                self.one_device_found = True
                self.found_devices.append(device)
        
        if self.one_device_found:
            print("⏳ Scan complete. New devices listed.\n")
        else:
            print("❌ No ESP32 devices found.\n")
            
        return self.found_devices

    async def connect(self, device):
        print(f"connect click")
        self.client = BleakClient(device.address, disconnected_callback=self.on_disconnected)
        try:
            await self.client.connect()
            if self.client.is_connected:
                self.connected_device = device
                print(f"🔗 Successfully connected to {device.name} [{device.address}]")
            else:
                print("❌ Failed to establish connection !")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            self.client = None
            self.connected_device = None

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Disconnected from device")
        self.client = None
        self.connected_device = None

    def on_disconnected(self, client):
        print("📴 Device disconnected!")
        self.connected_device = None
        self.client = None

        # Déclencher la mise à jour de l'interface (async)
        if self.on_disconnect_callback:
            import asyncio
            asyncio.create_task(self.on_disconnect_callback())

    async def send_command(self, command):
        if self.client and self.client.is_connected:
            await self.client.write_gatt_char(self.write_char_uuid, command.encode())
        else:
            print("❌ Cannot send command: no device connected.")

    async def start_notifications(self, on_message):
        if self.client and self.client.is_connected:
            await self.client.start_notify(self.notify_char_uuid, on_message)
        else:
            print("❌ Cannot start notifications: device not connected.")

    # def on_disconnected(self, client):
    #     if self.on_disconnect_callback:
    #         import asyncio
    #         asyncio.create_task(self.on_disconnect_callback())
