from bleak import BleakScanner, BleakClient

class BLEManager:
    def __init__(self):
        self.client = None
        self.connected_device = None
        self.found_devices = []
        self.one_device_found = False

    async def scan_devices(self):
        print("⏳ Scanning...")
        devices = await BleakScanner.discover(timeout=5.0)
    
        for device in devices:
            if device.name and device.name.startswith("ESP32"):
                print(f"📡 Found: {device.name} - {device.address}")
                self.one_device_found = True
                self.found_devices.append(device)
        
        if self.one_device_found:
            print("⏳ Scan complete. New devices listed.\n")
        else:
            print("❌ No devices found.\n")
            
        return self.found_devices

    async def connect(self, device):
        self.client = BleakClient(device.address)
        try:
            await self.client.connect()
            if await self.client.is_connected():
                self.connected_device = device
                print(f"Connected to {device.name} [{device.address}]")
            else:
                print("❌ Échec de la connexion")
        except Exception as e:
            print(f"Erreur lors de la connexion : {e}")
            self.client = None
            self.connected_device = None

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            self.connected_device = None
            print("Disconnected !")

    async def send_command(self, command):
        # envoie une commande au device connecté
        pass

    async def receive_message(self):
        # reçoit une réponse
        pass
