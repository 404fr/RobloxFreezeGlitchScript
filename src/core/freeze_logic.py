import time
import threading

# Try-except blocks for dependencies that might fail in headless/linux environments without display
try:
    import pyautogui
except (ImportError, KeyError):
    pyautogui = None

try:
    from pynput import keyboard
    import pynput.mouse
except (ImportError, KeyError):
    keyboard = None
    pynput = None

try:
    import mouse
except (ImportError, OSError):
    mouse = None

class FreezeTool:
    def __init__(self, status_callback=None):
        self.saved_coordinates = None
        self.saved_coordinatesBefore = None
        self.f3_pressed = False
        self.freeze_event = threading.Event()
        self.worker_thread = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.running = False
        self.status_callback = status_callback

    def log(self, message):
        print(message)
        if self.status_callback:
            self.status_callback(message)

    def start_tool(self):
        if not self.running:
            if not keyboard:
                self.log("Error: pynput.keyboard not available (headless environment?)")
                return

            self.running = True
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            # Start worker thread
            if self.worker_thread is None or not self.worker_thread.is_alive():
                self.worker_thread = threading.Thread(target=self._spacebar_worker, daemon=True)
                self.worker_thread.start()

            self.log("Tool started. Move mouse and press 'Q' to save coordinates.")

    def stop_tool(self):
        if self.running:
            self.running = False
            self.freeze_event.set() # Wake up thread so it can exit
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            self.freeze_event.clear()
            if self.mouse_listener:
                self.mouse_listener.stop()

            # Reset state
            if self.f3_pressed and mouse:
                mouse.release('left')
                if self.saved_coordinatesBefore:
                    mouse.move(*self.saved_coordinatesBefore)

            self.f3_pressed = False
            self.log("Tool stopped.")

    def _spacebar_worker(self):
        if not keyboard:
            return
        # Create a controller instance for this thread
        kb = keyboard.Controller()
        while self.running:
            if self.freeze_event.wait(timeout=0.1):
                if not self.running: break
                # Check again if we should be pressing (event is set)
                if self.freeze_event.is_set():
                    kb.press(keyboard.Key.space)
                    time.sleep(0.1)
                    kb.release(keyboard.Key.space)
                    time.sleep(0.1)

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char and key.char.lower() == 'q' and self.saved_coordinates is None:
                if pyautogui:
                    self.saved_coordinates = pyautogui.position()
                    self.log(f"Saved coordinates: {self.saved_coordinates}. Press F3 to freeze.")
                else:
                    self.log("Error: pyautogui not available")
        except AttributeError:
            pass

        if key == keyboard.Key.f3 and self.saved_coordinates is not None:
            self.toggle_freeze()

    def toggle_freeze(self):
        self.f3_pressed = not self.f3_pressed
        if self.f3_pressed:
            if pyautogui:
                self.saved_coordinatesBefore = pyautogui.position()

            self.log("Freeze ENABLED")

            if mouse:
                mouse.release('left')
                mouse.release('right')
                if self.saved_coordinates:
                    mouse.move(*self.saved_coordinates)
                mouse.press('left')

            self.freeze_event.set()

            # Start mouse listener to suppress movement
            if pynput:
                self.mouse_listener = pynput.mouse.Listener(suppress=True)
                self.mouse_listener.start()
        else:
            self.log("Freeze DISABLED")
            self.freeze_event.clear()
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None

            if mouse:
                mouse.release('left')
                if self.saved_coordinatesBefore:
                    mouse.move(*self.saved_coordinatesBefore)
