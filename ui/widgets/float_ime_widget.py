"""
输入法风格的悬浮窗组件
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class FloatIMEWidget(QWidget):
    """输入法风格悬浮窗"""
    
    def __init__(self, name, price, percent, is_up=True):
        super().__init__()
        self.init_ui(name, price, percent, is_up)
        self.setup_window_flags()
        
    def init_ui(self, name, price, percent, is_up):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        
        font_family = '"Segoe UI", "Microsoft YaHei", sans-serif'
        
        # 股票名称
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: #ffffff; font-family: {font_family}; font-size: 13px;")
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("background-color: #555; max-width: 1px; max-height: 12px; border: none;")
        
        # 价格
        price_label = QLabel(price)
        price_label.setStyleSheet(f"""
            color: {'#ff4d4f' if is_up else '#52c41a'};
            font-family: {font_family};
            font-size: 13px;
            font-weight: bold;
        """)
        
        # 涨跌幅（带箭头）
        arrow = "▲" if is_up else "▼"
        percent_with_arrow = f"{arrow} {percent}"
        percent_label = QLabel(percent_with_arrow)
        percent_label.setStyleSheet(f"""
            color: {'#ff4d4f' if is_up else '#52c41a'};
            font-family: {font_family};
            font-size: 13px;
            font-weight: bold;
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(divider)
        layout.addWidget(price_label)
        layout.addWidget(percent_label)
        
        self.setLayout(layout)
        
        # 设置样式 - 模拟毛玻璃效果 (半透明黑底 + 边框)
        self.setStyleSheet("""
            FloatIMEWidget {
                background-color: rgba(32, 32, 32, 0.9);
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # 自适应大小
        self.adjustSize()
        
    def setup_window_flags(self):
        """设置窗口标志"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def mousePressEvent(self, event):
        """实现拖拽功能"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        """处理窗口拖拽"""
        if hasattr(self, 'drag_start_position') and event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + diff)
            self.drag_start_position = event.globalPosition().toPoint()