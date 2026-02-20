"""
RoFreeze Main Window - Enhanced UI with northern lights theming.
"""

import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QIcon, QPen, QPainterPath, QRegion, QBitmap

from src.core.freeze_logic import FreezeTool
from src.ui import blur_window as BlurWindow
from src.ui.widgets import ModernButton, KeyButton, StatusBadge, ToggleSwitch
from src.ui.animated_logo import AnimatedLogo
from src.ui.particles import ParticleSystem
from src.ui.animations import AnimationHelper

class GradientLabel(QLabel):
    """Label with gradient text support."""
    def __init__(self, text, parent=None, size=28):
        super().__init__(text, parent)
        font = QFont("Segoe UI", size)
        font.setBold(True)
        self.setFont(font)
        self._colors = [QColor(34, 211, 238), QColor(34, 211, 238)] # Default solid
    
    def set_gradient_colors(self, c1, c2):
        self._colors = [c1, c2]
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, self._colors[0])
        gradient.setColorAt(1, self._colors[1])
        
        pen = QPen()
        pen.setBrush(gradient)
        painter.setPen(pen)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


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
        self.resize(380, 575)
        self.center()
        self._update_window_mask()

        # Apply glass effect after window handle exists
        QTimer.singleShot(100, self.enable_acrylic)
        
        # Entrance Animation
        self.setWindowOpacity(0.0)
        self._entrance_anim = QTimer.singleShot(200, self.animate_entrance)

    def _update_window_mask(self):
        """Clip bg_container and all its children to the rounded-rect shape.

        setMask() on the main window is ineffective when WA_TranslucentBackground
        is active because that attribute sets WS_EX_LAYERED, and Windows does not
        allow SetWindowRgn on layered windows.  Applying the mask to bg_container
        (a plain child widget) works correctly and clips every child widget too.
        """
        if not hasattr(self, 'bg_container'):
            return
        w, h = self.width(), self.height()
        bitmap = QBitmap(w, h)
        bitmap.fill(Qt.GlobalColor.color0)          # fully transparent
        p = QPainter(bitmap)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.color1)           # opaque inside
        p.drawRoundedRect(0, 0, w, h, 20, 20)
        p.end()
        self.bg_container.setMask(bitmap)

    def animate_entrance(self):
        """Fade in and slide up slightly."""
        # Fade in
        try:
            self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
            self.opacity_anim.setDuration(500)
            self.opacity_anim.setStartValue(0.0)
            self.opacity_anim.setEndValue(1.0)
            self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.opacity_anim.start()
        except Exception as e:
            print(f"Animation setup failed: {e}")
            self.setWindowOpacity(1.0)
        
        # Staggered reveal for children
        widgets = [self.animated_logo, self.title_label,
                  self.status_badge, self.toggle_btn, self.fp_card,
                  self.key_q_btn, self.key_f3_btn]
        
        for i, widget in enumerate(widgets):
            # Initially invisible
            op = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(op)
            op.setOpacity(0)
            
            # Fade in sequence
            QTimer.singleShot(100 + (i * 80), lambda w=widget, e=op: self._fade_widget(w, e))
            
    def _fade_widget(self, widget, effect):
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(600)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.start()
        # Keep reference to avoid gc
        setattr(widget, '_fade_anim', anim)

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
            # On Windows 11, let DWM round the window corners so the acrylic
            # effect doesn't bleed into the transparent corner areas.
            BlurWindow.apply_rounded_corners(hwnd)
        except Exception as e:
            print(f"Error applying acrylic: {e}")

    def init_ui(self):
        # Main container
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Background container
        self.bg_container = QWidget()
        self.bg_container.setObjectName("BgContainer")
        main_layout.addWidget(self.bg_container)

        self._setup_background()

        # Content overlay
        content_layout = QVBoxLayout(self.bg_container)
        content_layout.setContentsMargins(24, 20, 24, 24)
        content_layout.setSpacing(0)

        self.bg_container.setStyleSheet("""
            #BgContainer {
                background-color: rgba(10, 21, 32, 180);
                border-radius: 20px;
            }
        """)

        # === Header: close btn (left) + status badge (right) ===
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.close_btn = QPushButton("✕")
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

        self.status_badge = StatusBadge()
        self.status_badge.set_status("ready", "Ready")

        header_layout.addWidget(self.close_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        content_layout.addLayout(header_layout)

        content_layout.addSpacing(10)

        # === Animated Logo ===
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.animated_logo = AnimatedLogo(size=80)
        self.animated_logo.start_animations()
        logo_layout.addWidget(self.animated_logo)

        content_layout.addWidget(logo_container)

        content_layout.addSpacing(16)

        # === Title ===
        self.title_label = GradientLabel("ROFREEZE", size=30)
        self.title_label.set_gradient_colors(QColor(34, 211, 238), QColor(45, 212, 191))
        content_layout.addWidget(self.title_label)

        content_layout.addStretch()

        # Particles (send to back)
        self.particles = ParticleSystem(self.bg_container, count=25)
        self.particles.lower()

        # === Toggle Button ===
        self.toggle_btn = ModernButton("Get Started")
        self.toggle_btn.setToolTip("Start or stop the freeze macro")
        self.toggle_btn.clicked.connect(self.toggle_tool)
        content_layout.addWidget(self.toggle_btn)

        content_layout.addSpacing(12)

        # === First Person / Mouse Lock Settings Card ===
        self.fp_card = QFrame()
        self.fp_card.setObjectName("FpCard")
        self.fp_card.setStyleSheet("""
            QFrame#FpCard {
                background-color: rgba(255, 255, 255, 8);
                border: 1px solid rgba(255, 255, 255, 18);
                border-radius: 12px;
            }
        """)
        fp_card_layout = QHBoxLayout(self.fp_card)
        fp_card_layout.setContentsMargins(14, 10, 14, 10)
        fp_card_layout.setSpacing(8)

        fp_label = QLabel("First Person / Mouse Lock")
        fp_label.setStyleSheet("color: rgba(200, 210, 220, 210); background: transparent; border: none;")
        fp_label.setFont(QFont("Segoe UI", 10))

        self.fp_toggle = ToggleSwitch()
        self.fp_toggle.setToolTip(
            "Enable when playing in first-person or with mouse lock active.\n"
            "Skips cursor repositioning and movement suppression."
        )
        self.fp_toggle.toggled.connect(self._on_fp_toggle)

        fp_card_layout.addWidget(fp_label)
        fp_card_layout.addStretch()
        fp_card_layout.addWidget(self.fp_toggle)
        content_layout.addWidget(self.fp_card)

        content_layout.addSpacing(16)

        # === Key Buttons Row ===
        key_row = QWidget()
        key_layout = QHBoxLayout(key_row)
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.setSpacing(12)

        self.key_q_btn = KeyButton("Q", "Set Point", tooltip="Press Q to set the freeze point")
        self.key_f3_btn = KeyButton("F3", "Toggle", tooltip="Press F3 to toggle freeze")

        key_layout.addWidget(self.key_q_btn)
        key_layout.addWidget(self.key_f3_btn)
        content_layout.addWidget(key_row)

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

            clip_path = QPainterPath()
            clip_path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
            painter.setClipPath(clip_path)
            
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
        self._update_window_mask()
        self._cached_bg_pixmap = None  # Invalidate cache
        
        # Resize particles to match container
        if hasattr(self, 'particles'):
            self.particles.resize(self.bg_container.size())
            
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
            self.status_badge.set_status("frozen", message)
        elif "running" in lower_msg or "started" in lower_msg:
            self.status_badge.set_status("running", message)
        elif "stopped" in lower_msg:
            self.status_badge.set_status("stopped", message)
            self._update_theme("stopped")
        elif "point set" in lower_msg or "saved" in lower_msg:
            # Brief visual feedback on key button
            self.key_q_btn.set_pressed(True)
            QTimer.singleShot(300, lambda: self.key_q_btn.set_pressed(False))
            self.status_badge.set_status("running", message)
        else:
            self.status_badge.set_status("ready", message)
            self._update_theme("ready")

    def _update_theme(self, status):
        """Update window colors based on state."""
        style = ""
        c1, c2 = QColor(34, 211, 238), QColor(45, 212, 191) # Default Teal/Cyan
        
        if status == "running":
            # Purple/Cyan energy
            style = """
                #BgContainer {
                    background-color: rgba(15, 20, 35, 190);
                    border-radius: 20px;
                }
            """
            c1, c2 = QColor(168, 85, 247), QColor(34, 211, 238)

        elif status == "frozen":
            # Icy Blue
            style = """
                #BgContainer {
                    background-color: rgba(10, 25, 40, 190);
                    border-radius: 20px;
                }
            """
            c1, c2 = QColor(96, 165, 250), QColor(196, 235, 255)

        else: # Ready / Stopped
            style = """
                #BgContainer {
                    background-color: rgba(10, 21, 32, 180);
                    border-radius: 20px;
                }
            """
            c1, c2 = QColor(34, 211, 238), QColor(45, 212, 191)
            
        self.bg_container.setStyleSheet(style)
        self.title_label.set_gradient_colors(c1, c2)
        
        # Update button primary color via property if needed, but for now we rely on its internal state logic
        # or we could extend ModernButton to accept a theme color.
        # For simplicity, we keep the button consistent or let it handle its active state.

    def toggle_tool(self):
        if not self._is_running:
            self.logic.start_tool()
            self._is_running = True
            self.toggle_btn.setText("Stop")
            self.toggle_btn.set_active(True)
            self.animated_logo.set_active(True)
            self.status_badge.set_status("running", "Running...")
        else:
            self.logic.stop_tool()
            self._is_running = False
            self.toggle_btn.setText("Get Started")
            self.toggle_btn.set_active(False)
            self.animated_logo.set_active(False)
            self.status_badge.set_status("ready", "Stopped")

    def _on_fp_toggle(self, checked: bool):
        """Propagate first-person mode setting to the logic layer."""
        self.logic.first_person_mode = checked

    def close_app(self):
        self.logic.stop_tool()
        self.close()
