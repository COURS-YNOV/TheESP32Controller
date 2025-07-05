from nicegui import ui
from ble.manager import BLEManager
from config.config import APP_NAME

ble_devices = []
ble_manager = BLEManager()
commands_buttons = []
ui_elements = {}

def build_ui():
    ui.label(APP_NAME)

    with ui.row():
        ui.button('Scan BLE Devices', on_click=on_scan_click)
    
    global devices_dropdown
    devices_dropdown = ui.select(options=[], label='Detected device(s) :', clearable=True)

    with ui.row():
        ui_elements['connect_button'] = ui.button('Connect', on_click=on_connect_click).props('color=green')
        ui_elements['disconnect_button'] = ui.button('Disconnect', on_click=on_disconnect_click).props('color=red')
        ui_elements['connect_button'].disable()
        ui_elements['disconnect_button'].disable()

    with ui.row():
        for label, command in [
            ('LED_R', 'LED_R'),
            ('LED_G', 'LED_G'),
            ('BUZZER', 'BUZZER'),
            ('NTC', 'CTN'),
            ('INA237', 'INA'),
            ('TMP126', 'TEMP'),
            ('SCAN I2C', 'I2C'),
            ('WRITE LOG', 'W_LOG'),
            ('READ LOG', 'R_LOG'),
        ]:
            btn = ui.button(label, on_click=make_test_command_handler(command))
            commands_buttons.append(btn) 
        is_commands_buttons_activable()

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
        ui_elements['connect_button'].enable()

async def on_connect_click():
    print("ui_elements:", ui_elements)
    selected_name = devices_dropdown.value
    devices_dropdown.options = [f"{device.name} ({device.address})" for device in ble_devices]

    if not selected_name:
        ui.notify('❌ No selected device !', color='red')
        return

    device = next((device for device in ble_devices if f"{device.name} ({device.address})" == selected_name), None)
    if device is None:
        ui.notify('🔎 Device found !', color='red')
        return

    try:
        await ble_manager.connect(device)
        await ble_manager.start_notifications(on_receive)
        is_commands_buttons_activable(True)
        ui_elements['disconnect_button'].enable()
        ui_elements['connect_button'].enable()
        ui.notify(f'🔗 Connected to {selected_name}', color='green')
    except Exception as e:
        ui.notify(f'❌ Connexion error : {e}', color='red')

async def on_disconnect_click():
    try:
        await ble_manager.disconnect()
        is_commands_buttons_activable(False)
        ui.notify(f'❌ Device deconnected !', color='blue')
    except Exception as e:
        ui.notify(f'❌ Device deconnected : {e}', color='red')

def make_test_command_handler(command: str):
    async def handler():
        try:
            if(ble_manager.client != None):
                await ble_manager.send_command(command)
                ui.notify(f'✔️ Command "{command}" sent!', color='blue')
            else:
                ui.notify(f'📵 No device connected !', color='blue')
        except Exception as e:
            ui.notify(f'❌ Failed to send "{command}" : {e}', color='red')
    return handler

async def on_receive(_, data: bytearray):
    message = data.decode()
    print(f"📩 From ESP32 : {message}")
    #acknowledge_output.set_text(message)  # Mettre à jour une zone texte NiceGUI

def is_commands_buttons_activable(state = False):
      for btn in commands_buttons:
            if(state):
                btn.enable()
            else:
                btn.disable()