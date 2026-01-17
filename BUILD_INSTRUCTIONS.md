# Instructions for Building RoFreeze

## Prerequisites
1.  **Windows 10 or 11** (Required for the Acrylic Glass Effect).
2.  **Python 3.8+** installed.
3.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Building the Executable (Windows)

To create a standalone `.exe` file that includes the GUI and logic, it is recommended to use the provided spec file.

1.  Open a terminal (Command Prompt or PowerShell) in the project directory.
2.  Run PyInstaller with `RoFreeze.spec`:
    ```bash
    pyinstaller RoFreeze.spec
    ```
    *Note: This uses the configuration defined in `RoFreeze.spec`, which ensures all assets (images, logic files) are correctly included.*

3.  The executable will be located in the `dist` folder: `dist\RoFreeze.exe`.

### Alternative (Manual Command)
If you prefer to run the command manually (not recommended as it's harder to maintain):
```bash
pyinstaller --noconfirm --onefile --windowed --name "RoFreeze" --add-data "src/core/freeze_logic.py;src/core" --add-data "src/ui/blur_window.py;src/ui" --add-data "RoFreezeIcon.png;." --add-data "johny-goerend-NorthenLight-unsplash.jpg;." main.py
```

## Running from Source
```bash
python main.py
```
