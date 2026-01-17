"""
Enhanced widgets for RoFreeze UI.
Provides styled buttons with gradients, glow effects, and animations.
"""

from PyQt6.QtWidgets import QPushButton, QLabel, QWidget, QHBoxLayout
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QLinearGradient, QPen
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect


class ModernButton(QPushButton):
    """Enhanced button with gradient, glow, and hover animations."""
    
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(50)
        self._is_primary = is_primary
        self._hover_progress = 0.0
        self._is_active = False
        
        font = QFont("Segoe UI", 11)
        font.setBold(True)
        self.setFont(font)
        
        # Setup hover animation
        self._hover_anim = QPropertyAnimation(self, b"hoverProgress")
        self._hover_anim.setDuration(150)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._apply_style()
    
    @pyqtProperty(float)
    def hoverProgress(self):
        return self._hover_progress
    
    @hoverProgress.setter
    def hoverProgress(self, value):
        self._hover_progress = value
        self.update()
    
    def _apply_style(self):
        """Apply base stylesheet."""
        if self._is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border-radius: 25px;
                    border: 2px solid rgba(34, 211, 238, 0.5);
                    padding: 0 30px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border-radius: 20px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 10);
                    color: white;
                }
            """)
    
    def set_active(self, active: bool):
        """Set button active state (changes color scheme)."""
        self._is_active = active
        self.update()
    
    def enterEvent(self, event):
        """Animate hover in."""
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animate hover out."""
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Custom paint with gradient and glow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = 25
        
        if self._is_primary:
            # Create gradient based on state
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            
            if self._is_active:
                # Active state: teal gradient
                gradient.setColorAt(0, QColor(13, 59, 102))  # Deep blue
                gradient.setColorAt(1, QColor(34, 211, 238))  # Cyan
            else:
                # Normal state: subtle dark gradient
                base_alpha = int(60 + (self._hover_progress * 40))
                gradient.setColorAt(0, QColor(40, 40, 50, base_alpha + 100))
                gradient.setColorAt(1, QColor(60, 60, 70, base_alpha + 100))
            
            # Draw glow on hover
            if self._hover_progress > 0:
                glow_color = QColor(34, 211, 238)
                glow_alpha = int(self._hover_progress * 80)
                glow_color.setAlpha(glow_alpha)
                
                # Outer glow
                glow_rect = rect.adjusted(-4, -4, 4, 4)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow_color)
                painter.drawRoundedRect(glow_rect, radius + 4, radius + 4)
            
            # Draw button background
            painter.setBrush(gradient)
            
            # Border
            border_color = QColor(34, 211, 238)
            border_alpha = int(80 + self._hover_progress * 175)
            border_color.setAlpha(border_alpha)
            painter.setPen(QPen(border_color, 2))
            
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)
        
        # Draw text
        painter.setPen(QColor(255, 255, 255))
        font = self.font()
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
        painter.end()


class KeyBadge(QWidget):
    """Styled keyboard shortcut badge."""
    
    def __init__(self, key: str, label: str = "", parent=None, tooltip: str = ""):
        super().__init__(parent)
        self._key = key
        self._label = label
        self._pressed = False
        
        self.setFixedSize(80, 70)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if tooltip:
            self.setToolTip(tooltip)

        # Set accessible name for screen readers
        self.setAccessibleName(f"Key {key}, {label}")

        # Pre-calculate fonts and rects
        self._key_font = QFont("Segoe UI", 14)
        self._key_font.setBold(True)
        self._label_font = QFont("Segoe UI", 8)
        self._label_font.setBold(False)

        self._key_rect = QRect(15, 5, 50, 40)
        self._label_rect = QRect(0, 48, 80, 20)

        # Pre-create common colors/pens/brushes?
        # Colors are cheap, but we can avoid recreating QColor(34, 211, 238, 150) every time
        self._pressed_bg = QColor(34, 211, 238, 150)
        self._pressed_pen = QPen(QColor(34, 211, 238), 2)
        self._normal_bg = QColor(40, 40, 50, 150)
        self._normal_pen = QPen(QColor(100, 100, 120), 1)
        self._text_color = QColor(255, 255, 255)
        self._label_color = QColor(150, 150, 160)
    
    def set_pressed(self, pressed: bool):
        """Visual feedback for key press."""
        self._pressed = pressed
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        if self._pressed:
            painter.setBrush(self._pressed_bg)
            painter.setPen(self._pressed_pen)
        else:
            painter.setBrush(self._normal_bg)
            painter.setPen(self._normal_pen)
        
        painter.drawRoundedRect(self._key_rect, 8, 8)
        
        # Key text
        painter.setPen(self._text_color)
        painter.setFont(self._key_font)
        painter.drawText(self._key_rect, Qt.AlignmentFlag.AlignCenter, self._key)
        
        # Label below
        if self._label:
            painter.setPen(self._label_color)
            painter.setFont(self._label_font)
            painter.drawText(self._label_rect, Qt.AlignmentFlag.AlignCenter, self._label)
        
        painter.end()


class StatusIndicator(QWidget):
    """Animated status indicator with pulsing ring."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = "ready"  # ready, running, frozen
        self._pulse = 0.0
        self._text = "Ready"
        
        self.setFixedSize(200, 40)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Pulse animation
        self._pulse_anim = QPropertyAnimation(self, b"pulse")
        self._pulse_anim.setDuration(1200)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Status colors
        self._colors = {
            "ready": QColor(150, 150, 160),
            "running": QColor(34, 211, 238),
            "frozen": QColor(45, 212, 191),
            "stopped": QColor(200, 100, 100)
        }

        # Cached font and rects
        self._font = QFont("Segoe UI", 10)
        self._font.setBold(True)
        self._text_rect = QRect(50, 0, 150, 40)

    def resizeEvent(self, event):
        self._text_rect = QRect(50, 0, 150, self.height())
        super().resizeEvent(event)
    
    @pyqtProperty(float)
    def pulse(self):
        return self._pulse
    
    @pulse.setter
    def pulse(self, value):
        self._pulse = value
        self.update()
    
    def set_status(self, status: str, text: str = ""):
        """Update status and text."""
        self._status = status
        self._text = text or status.capitalize()
        
        if status in ("running", "frozen"):
            self._pulse_anim.start()
        else:
            self._pulse_anim.stop()
            self._pulse = 0.0
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = 25
        center_y = self.height() // 2
        
        color = self._colors.get(self._status, self._colors["ready"])
        
        # Draw pulsing rings for active states
        if self._status in ("running", "frozen"):
            ring_color = QColor(color)
            ring_alpha = int((1 - self._pulse) * 150)
            ring_color.setAlpha(ring_alpha)
            
            ring_radius = int(8 + self._pulse * 12)
            painter.setPen(QPen(ring_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center_x - ring_radius, center_y - ring_radius,
                               ring_radius * 2, ring_radius * 2)
        
        # Draw center dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(center_x - 6, center_y - 6, 12, 12)
        
        # Draw text
        painter.setPen(color)
        painter.setFont(self._font)
        painter.drawText(self._text_rect, Qt.AlignmentFlag.AlignVCenter |
                        Qt.AlignmentFlag.AlignLeft, self._text)
        
        painter.end()
