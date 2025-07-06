from nicegui import ui
from ble.manager import BLEManager
from config.config import APP_NAME

ble_devices = []
ble_manager = BLEManager()
commands_buttons = []
ui_elements = {}

def build_ui():
    with ui.row().classes('justify-center w-full'):
        ui.label(APP_NAME).classes('text-xl font-bold mb-4')

    with ui.column().classes('p-4 bg-gray-100 rounded-lg shadow-md items-center w-full'):
        ui.label('📡 Scan Devices').classes('text-lg font-semibold mb-4')

        with ui.row().classes('items-center gap-4'):
            ui.button('🔍 Scan BLE Devices', on_click=on_scan_click)
            global devices_dropdown
            devices_dropdown = ui.select(
                options=[], 
                label='Detected device(s) :', 
                clearable=True
            ).classes('w-80')  # largeur fixe

        with ui.row():
            ui_elements['connect_button'] = ui.button('Connect', on_click=on_connect_click).props('color=green')
            ui_elements['disconnect_button'] = ui.button('Disconnect', on_click=on_disconnect_click).props('color=red')
            ui_elements['connect_button'].disable()
            ui_elements['disconnect_button'].disable()

    with ui.column().classes('p-4 bg-gray-100 rounded-lg shadow-md items-center w-full'):
        ui.label('🚀 Launch Tests').classes('text-lg font-semibold mb-4')

        with ui.row().classes('justify-center items-start gap-8 max-w-5xl w-full'):
            with ui.grid(columns=3).classes('gap-2 min-h-40'):
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
            ack_output = ui.textarea(label='Acknowledgment from ESP32').props('readonly').classes('w-80')
    
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
    global ack_output
    ack_output.value = (ack_output.value or '') + message + '\n'
    ack_output.update()
    # TODO add function to automatically scroll at the bottom of the field 

def is_commands_buttons_activable(state = False):
      for btn in commands_buttons:
            if(state):
                btn.enable()
            else:
                btn.disable()