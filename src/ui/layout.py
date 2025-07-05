from nicegui import ui
from ble.manager import BLEManager
from config.config import APP_NAME

ble_devices = []
ble_manager = BLEManager()

def build_ui():
    ui.label(APP_NAME)

    with ui.row():
        ui.button('Scan BLE Devices', on_click=on_scan_click)
    
    global devices_dropdown
    devices_dropdown = ui.select(options=[], label='Devices détectés', clearable=True)

    with ui.row():
        ui.button('Connect', on_click=on_connect_click)

    global ack_output
    ack_output = ui.textarea(label='Messages de retour')
    ack_output.props('readonly')

async def on_scan_click():
    global ble_devices
    ble_devices = await ble_manager.scan_devices()
    options = [
        f"{d.name or 'Unknown'} ({d.address})"
        for d in ble_devices if d.name or d.address
    ]
    if not options:
        ui.notify("❌ No BLE device detected !")
    else:
        devices_dropdown.options = options
        devices_dropdown.update()
        ui.notify(f"{len(options)} device(s) detected !")

async def on_connect_click():
    selected_name = devices_dropdown.value
    devices_dropdown.options = [f"{d.name} ({d.address})" for d in ble_devices]

    print(selected_name)
    print(ble_devices)
    if not selected_name:
        ui.notify('Aucun périphérique sélectionné', color='red')
        return

    device = next((d for d in ble_devices if f"{d.name} ({d.address})" == selected_name), None)
    if device is None:
        ui.notify('Périphérique non trouvé dans la liste', color='red')
        return

    try:
        await ble_manager.connect(device)
        ui.notify(f'Connecté à {selected_name}', color='green')
    except Exception as e:
        ui.notify(f'Erreur de connexion : {e}', color='red')