## 2024-05-22 - PyQt Render Loop Optimization
**Learning:** In PyQt custom widgets, instantiating `QColor`, `QFont`, or `QRect` objects inside `paintEvent` can cause measurable performance overhead, especially for animated widgets that repaint frequently (e.g. 60fps).
**Action:** Always pre-allocate static graphics resources in `__init__` or update them in `resizeEvent` (for geometry-dependent objects).
