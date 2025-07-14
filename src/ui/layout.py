from nicegui import ui
from ble.manager import BLEManager
from config.config import APP_NAME, UI_COMMANDS_BUTTON, UI_COMMAND_SLIDER_BUTTON, UI_COMMAND_FREE_TEXT_BUTTON

ble_devices = []
ble_manager = BLEManager()
ui_commands = []
ui_elements = {}

def build_ui():
    with ui.row().classes('justify-center w-full'):
        ui.label(APP_NAME).classes('text-xl font-bold mb-4')
    
    global scan_section
    with ui.column().classes('p-4 rounded-lg shadow-md items-center w-full').style('background-color: #ffe8e8; border: 2px solid #FF6666;') as scan_section:
        ui.label('📡 Scan Devices').classes('text-lg font-semibold mb-4')

        with ui.row().classes('items-center gap-4'):
            ui.button('🔍 Scan BLE Devices', on_click=on_scan_click)
            global devices_dropdown
            devices_dropdown = ui.select(
                options=[], 
                label='Detected device(s) :', 
                clearable=True
            ).classes('w-80')

        with ui.row():
            ui_elements['connect_button'] = ui.button('Connect', on_click=on_connect_click).props('color=green')
            ui_elements['disconnect_button'] = ui.button('Disconnect', on_click=on_disconnect_click).props('color=red')
            ui_elements['connect_button'].disable()
            ui_elements['disconnect_button'].disable()

    with ui.column().classes('p-4 bg-gray-100 rounded-lg shadow-md items-center w-full'):
        ui.label('🚀 Launch Tests').classes('text-lg font-semibold mb-4')

        # --- Commmands Buttons Section ---
        with ui.row().classes('justify-center items-start gap-8 max-w-5xl w-full'):
            with ui.grid(columns=3).classes('gap-2 min-h-40'):
                for label, command in UI_COMMANDS_BUTTON:
                    btn = ui.button(label, on_click=make_test_command_handler(command))
                    ui_commands.append(btn)

            # --- Acknowledgement Section ---    
            global ack_output
            ack_output = ui.textarea(label='Acknowledgment from ESP32').props('readonly').classes('w-80')
        
        spacer()

        with ui.grid(columns=2).classes('gap-10 justify-center items-start'):
            # --- PWM Section ---
            with ui.column().classes('gap-4 p-4 rounded-lg shadow-md w-full').style('background-color: #f2f3ff'):
                ui.label('📈 PWM').classes('text-lg font-semibold text-center self-center')

                with ui.row().classes('items-center gap-4 w-full'):
                    slider = ui.slider(min=0, max=100, value=50).props('label-always') \
                        .classes('flex-1 mt-5')
                    btn_pwm = ui.button("SEND", on_click=make_test_command_handler(lambda: UI_COMMAND_SLIDER_BUTTON + str(slider.value))) \
                        .classes('h-12')
                    ui_commands.append(slider)
                    ui_commands.append(btn_pwm)
            
            # --- Free Text Section ---
            with ui.column().classes('gap-4 p-4 rounded-lg shadow-md w-full').style('background-color: #f2f3ff'):
                ui.label('📩 Free Text').classes('text-lg font-semibold text-center self-center')

                with ui.row().classes('items-center gap-4 w-full'):
                    input_cmd = ui.input(label='Command', placeholder='Start typing') \
                        .props('clearable dense') \
                        .classes('w-44 h-12')
                    btn_txt = ui.button("SEND", on_click=lambda: make_test_command_handler(lambda: UI_COMMAND_FREE_TEXT_BUTTON + str(input_cmd.value))()) \
                        .classes('h-12')
                    ui_commands.append(input_cmd)
                    ui_commands.append(btn_txt)
                 
    
    is_ui_commands_activable()

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
    if ble_manager.connected_device is None:
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
            is_ui_commands_activable(True)
            ui_elements['disconnect_button'].enable()
            ui_elements['connect_button'].disable()
            set_scan_section_background(True)
            ble_manager.on_disconnect_callback = handle_disconnect
            ui.notify(f'🔗 Connected to {selected_name}', color='green')
        except Exception as e:
            ui.notify(f'❌ Connexion error : {e}', color='red')

async def on_disconnect_click():
    try:
        await ble_manager.disconnect()
        is_ui_commands_activable(False)
        set_scan_section_background()
        ui_elements['disconnect_button'].disable()
        ui.notify(f'❌ Device deconnected !', color='blue')
    except Exception as e:
        ui.notify(f'❌ Device deconnected : {e}', color='red')

def make_test_command_handler(command: str):
    async def handler():
        try:
            cmd_str = command() if callable(command) else command
            if(ble_manager.client != None):
                await ble_manager.send_command(cmd_str)
                ui.notify(f'✔️ Command "{cmd_str}" sent!', color='blue')
            else:
                ui.notify(f'📵 No device connected !', color='blue')
        except Exception as e:
            ui.notify(f'❌ Failed to send "{cmd_str}" : {e}', color='red')
    return handler

async def on_receive(_, data: bytearray):
    message = data.decode()
    print(f"📩 From ESP32 : {message}")
    global ack_output
    ack_output.value = (ack_output.value or '') + message + '\n'
    ack_output.update()

def is_ui_commands_activable(state = False):
      for btn in ui_commands:
            if(state):
                btn.enable()
            else:
                btn.disable()

def spacer(height='1rem'):
    ui.element('div').style(f'height: {height};')

def set_scan_section_background(is_connected=False):
    if not is_connected:
        scan_section.style('background-color: #FFE5E5; border: 2px solid #FF6666;')
    else:
        scan_section.style('background-color: #E5FFE5; border: 2px solid #66CC66;')

async def handle_disconnect():
    print("⚠️ UI notified of BLE disconnection.")
    is_ui_commands_activable(False)
    ui_elements['disconnect_button'].disable()
    ui_elements['connect_button'].enable()
    set_scan_section_background(False)
