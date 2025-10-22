# client/network/message_handler.py

class MessageHandler:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback

    def handle_message(self, data):
        action = data.get("action")
        payload = data.get("payload")
        self.ui_callback(action, payload)
