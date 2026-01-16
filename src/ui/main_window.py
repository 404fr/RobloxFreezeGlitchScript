"""
RoFreeze Main Window - Enhanced UI with northern lights theming.
"""

import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QIcon

from src.core.freeze_logic import FreezeTool
from src.ui import blur_window as BlurWindow
from src.ui.widgets import ModernButton, KeyBadge, StatusIndicator
from src.ui.animated_logo import AnimatedLogo


class LogicBridge(QObject):
    """Bridge class to handle signals from logic threads."""
    status_update = pyqtSignal(str)


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup bridge for thread safety
        self.bridge = LogicBridge()
        self.bridge.status_update.connect(self.update_status_ui)

        # Initialize logic with the emit method of the signal
        self.logic = FreezeTool(status_callback=self.bridge.status_update.emit)

        self.drag_pos = None
        self._is_running = False
        self._cached_bg_pixmap = None

        self.init_ui()
        self.setup_window()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # In dev, relative to this file: src/ui/../../filename
            base_path = os.path.join(os.path.dirname(__file__), '..', '..')

        return os.path.join(base_path, relative_path)

    def setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set Window Icon
        icon_path = self.resource_path('RoFreezeIcon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Dimensions
        self.resize(380, 520)
        self.center()

        # Apply glass effect after window handle exists
        QTimer.singleShot(100, self.enable_acrylic)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def enable_acrylic(self):
        try:
            hwnd = int(self.winId())
            # Dark acrylic with teal tint
            BlurWindow.apply_acrylic(hwnd, hex_color="#0A1520", alpha=200)
        except Exception as e:
            print(f"Error applying acrylic: {e}")

    def init_ui(self):
        # Main container
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout with stacking for background
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Background container (for texture)
        self.bg_container = QWidget()
        self.bg_container.setObjectName("BgContainer")
        main_layout.addWidget(self.bg_container)
        
        # Load and set background texture
        self._setup_background()
        
        # Content overlay
        content_layout = QVBoxLayout(self.bg_container)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(15)
        
        # Apply styling to container
        self.bg_container.setStyleSheet("""
            #BgContainer {
                background-color: rgba(10, 21, 32, 180);
                border-radius: 20px;
                border: 1px solid rgba(34, 211, 238, 0.2);
            }
        """)
        
        # === Header with close button ===
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Close Application")
        self.close_btn.setAccessibleName("Close")
        self.close_btn.clicked.connect(self.close_app)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 5);
                color: #667788;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background: rgba(255, 100, 100, 50);
                color: #ffffff; 
            }
        """)
        header_layout.addWidget(self.close_btn)
        content_layout.addLayout(header_layout)
        
        # === Animated Logo ===
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.animated_logo = AnimatedLogo(size=70)
        self.animated_logo.start_animations()
        logo_layout.addWidget(self.animated_logo)
        
        content_layout.addWidget(logo_container)
        
        # === Title ===
        title_label = QLabel("RoFreeze")
        title_font = QFont("Segoe UI", 28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # === Description ===
        desc_label = QLabel("Macro to freeze the roblox client.")
        desc_font = QFont("Segoe UI", 10)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: rgba(180, 200, 220, 200);")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        content_layout.addSpacing(10)
        
        # === Keyboard Shortcuts ===
        shortcuts_container = QWidget()
        shortcuts_layout = QHBoxLayout(shortcuts_container)
        shortcuts_layout.setContentsMargins(0, 0, 0, 0)
        shortcuts_layout.setSpacing(20)
        shortcuts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.key_q = KeyBadge("Q", "Set Point", tooltip="Press Q to set the freeze point")
        self.key_f3 = KeyBadge("F3", "Toggle", tooltip="Press F3 to toggle freeze")
        
        shortcuts_layout.addWidget(self.key_q)
        shortcuts_layout.addWidget(self.key_f3)
        
        content_layout.addWidget(shortcuts_container)
        
        content_layout.addSpacing(5)
        
        # === Status Indicator ===
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_indicator = StatusIndicator()
        self.status_indicator.set_status("ready", "Ready")
        status_layout.addWidget(self.status_indicator)
        
        content_layout.addWidget(status_container)
        
        content_layout.addStretch()
        
        # === Action Button ===
        self.toggle_btn = ModernButton("Get Started")
        self.toggle_btn.setToolTip("Start or stop the freeze macro")
        self.toggle_btn.clicked.connect(self.toggle_tool)
        content_layout.addWidget(self.toggle_btn)
        
        content_layout.addSpacing(10)

    def _setup_background(self):
        """Setup the northern lights background texture with low opacity."""
        texture_path = self.resource_path('johny-goerend-NorthenLight-unsplash.jpg')
        
        if os.path.exists(texture_path):
            self._bg_pixmap = QPixmap(texture_path)
        else:
            self._bg_pixmap = None
    
    def paintEvent(self, event):
        """Paint background texture with low opacity."""
        super().paintEvent(event)
        
        if hasattr(self, '_bg_pixmap') and self._bg_pixmap and not self._bg_pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            if self._cached_bg_pixmap is None or self._cached_bg_pixmap.size() != self.size():
                # Scale pixmap to cover the window
                self._cached_bg_pixmap = self._bg_pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )

            # Center the image
            x = (self.width() - self._cached_bg_pixmap.width()) // 2
            y = (self.height() - self._cached_bg_pixmap.height()) // 2
            
            # Draw with very low opacity
            painter.setOpacity(0.12)
            painter.drawPixmap(x, y, self._cached_bg_pixmap)
            painter.end()

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self._cached_bg_pixmap = None  # Invalidate cache
        self.update()  # Trigger a repaint

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def update_status_ui(self, message):
        """Handle status updates from logic thread."""
        lower_msg = message.lower()
        
        if "frozen" in lower_msg or "freeze" in lower_msg:
            self.status_indicator.set_status("frozen", message)
        elif "running" in lower_msg or "started" in lower_msg:
            self.status_indicator.set_status("running", message)
        elif "stopped" in lower_msg:
            self.status_indicator.set_status("stopped", message)
        elif "point set" in lower_msg or "saved" in lower_msg:
            # Brief visual feedback on key badge
            self.key_q.set_pressed(True)
            QTimer.singleShot(300, lambda: self.key_q.set_pressed(False))
            self.status_indicator.set_status("running", message)
        else:
            self.status_indicator.set_status("ready", message)

    def toggle_tool(self):
        if not self._is_running:
            self.logic.start_tool()
            self._is_running = True
            self.toggle_btn.setText("Stop")
            self.toggle_btn.set_active(True)
            self.animated_logo.set_active(True)
            self.status_indicator.set_status("running", "Running...")
        else:
            self.logic.stop_tool()
            self._is_running = False
            self.toggle_btn.setText("Get Started")
            self.toggle_btn.set_active(False)
            self.animated_logo.set_active(False)
            self.status_indicator.set_status("ready", "Stopped")

    def close_app(self):
        self.logic.stop_tool()
        self.close()
