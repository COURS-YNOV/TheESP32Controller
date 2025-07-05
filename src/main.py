from nicegui import ui
from ui.layout import build_ui
from config.config import APP_NAME

if __name__ in {"__main__", "__mp_main__"}:
    # Build ui interface
    build_ui()
    # Launch app
    ui.run(title=APP_NAME, reload=True)
