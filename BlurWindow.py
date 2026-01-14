import sys
import ctypes
from ctypes import c_int, c_uint, c_void_p, Structure, POINTER, byref, sizeof
import platform

class AccentPolicy(Structure):
    _fields_ = [
        ("AccentState", c_int),
        ("AccentFlags", c_int),
        ("GradientColor", c_uint), # Changed to c_uint for safety
        ("AnimationId", c_int)
    ]

class WindowCompositionAttributeData(Structure):
    _fields_ = [
        ("Attribute", c_int),
        ("Data", POINTER(AccentPolicy)),
        ("SizeOfData", c_int)
    ]

# Windows 10 1803+ constants
WCA_ACCENT_POLICY = 19
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4 # Target

def hex_to_abgr(hex_color, alpha=128):
    """
    Converts a hex color string to ABGR integer format.
    GradientColor in AccentPolicy is expected to be ABGR.
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (alpha << 24) | (b << 16) | (g << 8) | r

def apply_acrylic(hwnd, hex_color="#1e1e1e", alpha=150):
    """
    Applies the Acrylic Blur effect to the given window handle (HWND).
    Safe to call on non-Windows systems (will do nothing).
    """
    if platform.system() != "Windows":
        return

    try:
        user32 = ctypes.windll.user32

        accent = AccentPolicy()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = hex_to_abgr(hex_color, alpha)
        accent.AccentFlags = 0
        accent.AnimationId = 0

        data = WindowCompositionAttributeData()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = sizeof(accent)

        user32.SetWindowCompositionAttribute(hwnd, byref(data))
    except Exception as e:
        print(f"Failed to apply acrylic effect: {e}")

def apply_blur(hwnd):
    """Fallback to standard blur if acrylic fails or simply preferred."""
    if platform.system() != "Windows":
        return

    try:
        user32 = ctypes.windll.user32
        accent = AccentPolicy()
        accent.AccentState = ACCENT_ENABLE_BLURBEHIND
        accent.GradientColor = 0

        data = WindowCompositionAttributeData()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = sizeof(accent)

        user32.SetWindowCompositionAttribute(hwnd, byref(data))
    except Exception:
        pass
