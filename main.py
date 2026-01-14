import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QPoint, QSize, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QCursor, QIcon

from FreezeLogic import FreezeTool
import BlurWindow

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(40)

        font = QFont("Segoe UI", 10)
        font.setBold(True)
        self.setFont(font)

        if is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(60, 60, 60, 200);
                    color: white;
                    border-radius: 20px;
                    border: 1px solid rgba(255, 255, 255, 30);
                }
                QPushButton:hover {
                    background-color: rgba(80, 80, 80, 200);
                    border: 1px solid rgba(255, 255, 255, 80);
                }
                QPushButton:pressed {
                    background-color: rgba(40, 40, 40, 200);
                }
            """)
        else:
             self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 10);
                    color: white;
                }
            """)

# Bridge class to handle signals
class LogicBridge(QObject):
    status_update = pyqtSignal(str)

class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup bridge for thread safety
        self.bridge = LogicBridge()
        self.bridge.status_update.connect(self.update_status_ui)

        # Initialize logic with the emit method of the signal
        # Logic runs in threads (pynput), so we must use signals to update UI
        self.logic = FreezeTool(status_callback=self.bridge.status_update.emit)

        self.drag_pos = None

        self.init_ui()
        self.setup_window()

    def setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Dimensions
        self.resize(360, 480)
        self.center()

        # Apply glass effect
        # We need to defer this slightly to ensure window handle exists
        QTimer.singleShot(100, self.enable_acrylic)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def enable_acrylic(self):
        try:
            hwnd = int(self.winId())
            # Use dark acrylic
            BlurWindow.apply_acrylic(hwnd, hex_color="#101010", alpha=180)
        except Exception as e:
            print(f"Error applying acrylic: {e}")

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        # Add a subtle border/background for systems where blur might fail or be too transparent
        central_widget.setStyleSheet("""
            #CentralWidget {
                background-color: rgba(20, 20, 20, 150);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title / Header
        # Close button top right
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_app)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { color: white; }
        """)
        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)

        layout.addStretch()

        # Main Graphic / Text Area
        # Imitating the "Design Smarter" text
        title_label = QLabel("Freeze Tool")
        title_font = QFont("Segoe UI", 24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel("Unlock powerful tools to freeze interactions.\nPress 'Q' to set point, 'F3' to toggle.")
        desc_font = QFont("Segoe UI", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #aaaaaa;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #FFFF00; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Action Button
        self.toggle_btn = ModernButton("Get Started")
        self.toggle_btn.clicked.connect(self.toggle_tool)
        layout.addWidget(self.toggle_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def update_status_ui(self, message):
        # This slot runs on the main thread
        self.status_label.setText(message)

    def toggle_tool(self):
        if not self.logic.running:
            self.logic.start_tool()
            self.toggle_btn.setText("Stop")
            self.status_label.setText("Running...")
        else:
            self.logic.stop_tool()
            self.toggle_btn.setText("Get Started")
            self.status_label.setText("Stopped")

    def close_app(self):
        self.logic.stop_tool()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Gui()
    window.show()
    sys.exit(app.exec())
