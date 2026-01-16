# RoFreeze - Developer & AI Agent Guide

## Project Overview
RoFreeze is a Python-based utility designed to perform a "freeze glitch" in Roblox. It works by automating mouse and keyboard interactions—specifically, it saves the mouse cursor position and then repeatedly presses the spacebar while preventing mouse movement. This action "freezes" the client in a specific state.

The application features a modern, acrylic-styled user interface built with PyQt6.

## Architecture
The project follows a clear separation of concerns:

- **`src/ui/`**: Contains all User Interface code.
  - `main_window.py`: The main entry point for the GUI. Handles the window setup, layout, and connects UI events to logic.
  - `blur_window.py`: Handles the Windows API calls necessary to achieve the acrylic/blur effect behind the window.
  - `widgets.py`: Custom styled Qt widgets (buttons, badges, indicators).
  - `animated_logo.py`: A custom painted animated logo widget.
- **`src/core/`**: Contains the application logic.
  - `freeze_logic.py`: The core logic class (`FreezeTool`). It manages the keyboard/mouse listeners and the freezing thread.

## Tech Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Input Handling**:
  - `pynput`: For global keyboard and mouse monitoring.
  - `pyautogui`: For retrieving mouse position.
  - `mouse`: For low-level mouse control (moving/clicking).
- **Packaging**: PyInstaller (see `RoFreeze.spec`).

## Key Files
- `main.py`: The application entry point. Initializes the `QApplication` and the `Gui`.
- `src/ui/main_window.py`: The UI controller. Note the use of `LogicBridge` and `pyqtSignal` to safely update the UI from background threads.
- `src/core/freeze_logic.py`: Contains the `FreezeTool` class. It starts listeners for 'Q' (save point) and 'F3' (toggle freeze).

## Development Guidelines

### 1. Threading & UI Safety
- The freeze logic runs in background threads to avoid blocking the GUI.
- **NEVER** update UI components directly from `src/core/freeze_logic.py` or any background thread.
- Use the `status_callback` in `FreezeTool` which emits a `pyqtSignal` in `main_window.py` to marshal the call back to the main UI thread.

### 2. Dependency Handling
- The application is often run in environments where display drivers might differ. `freeze_logic.py` includes try-except blocks for `pyautogui`, `pynput`, and `mouse` to handle potential import errors gracefully (though the core functionality requires them).

### 3. Windows Specifics
- The acrylic effect in `blur_window.py` relies on user32.dll and dwmapi.dll. This feature is Windows 10/11 specific.
- Development on non-Windows platforms is possible for logic, but the UI effects may not render correctly.

## Testing & Verification
- **Unit Testing**: Difficult for this project due to global input hooks.
- **Manual Verification**:
  1. Run `python main.py`.
  2. Click "Get Started".
  3. Focus on another window (e.g., Notepad).
  4. Press 'Q'. Verify the UI status updates to "Point set".
  5. Press 'F3'. Verify the mouse locks to the position and spacebar starts spamming (check in Notepad).
  6. Press 'F3' again to stop.

**Caution**: When testing the freeze functionality, be prepared to use the stop shortcut (F3) or close the application if input control is lost.
