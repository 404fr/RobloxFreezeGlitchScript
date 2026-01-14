# Instructions for Building FreezeTool

## Prerequisites
1.  **Windows 10 or 11** (Required for the Acrylic Glass Effect).
2.  **Python 3.8+** installed.
3.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Building the Executable (Windows)

To create a standalone `.exe` file that includes the GUI and logic:

1.  Open a terminal (Command Prompt or PowerShell) in the project directory.
2.  Run PyInstaller:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "FreezeTool" --add-data "FreezeLogic.py;." --add-data "BlurWindow.py;." main.py
    ```
    *Note: The separator for `--add-data` on Windows is `;`. On Linux/Mac it is `:`.*

3.  The executable will be located in the `dist` folder: `dist\FreezeTool.exe`.

## Running from Source
```bash
python main.py
```
