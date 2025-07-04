from nicegui import ui
from ble.manager import scan_ble_devices
from config.config import APP_NAME

# Variable pour stocker les devices détectés
ble_devices = []

def build_ui():
    ui.label(APP_NAME)

    with ui.row():
        ui.button('Scan BLE Devices', on_click=on_scan_click)
    
    global devices_dropdown
    devices_dropdown = ui.select(options=[], label='Devices détectés')

    global ack_output
    ack_output = ui.textarea(label='Messages de retour')
    ack_output.props('readonly')

async def on_scan_click():
    global ble_devices
    ble_devices = await scan_ble_devices()
    options = [
        f"{d.name or 'Unknown'} ({d.address})"
        for d in ble_devices if d.name or d.address
    ]
    if not options:
        devices_dropdown.update()
        ui.notify("❌ No BLE device detected !")
    else:
        devices_dropdown.options = options
        devices_dropdown.update()
        ui.notify(f"{len(options)} device(s) detected !")
