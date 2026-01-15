"""
迷你卡片风格的悬浮窗组件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPen, QColor


class DragHandle(QWidget):
    """拖拽手柄"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(20, 4)
        self.hide()  # 初始隐藏
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen()
        pen.setColor(QColor("#666"))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        painter.setPen(pen)
        painter.drawLine(2, 2, 18, 2)


class FloatCardWidget(QWidget):
    """迷你卡片风格悬浮窗"""
    
    def __init__(self, name, code, price, percent, is_up=True):
        super().__init__()
        self.drag_handle = DragHandle()
        self.init_ui(name, code, price, percent, is_up)
        self.setup_window_flags()
    
    def format_price(self, price):
        """格式化价格显示，防止过长"""
        if isinstance(price, str):
            try:
                price_float = float(price)
            except:
                return price[:8]  # 如果转换失败，截断显示
        else:
            price_float = price
        
        # 根据价格大小选择显示格式
        if price_float >= 1000:
            return f"{price_float:.1f}"  # 大于1000时显示1位小数
        elif price_float >= 100:
            return f"{price_float:.2f}"  # 100-1000显示2位小数
        else:
            return f"{price_float:.3f}"  # 小于100显示3位小数
        
    def init_ui(self, name, code, price, percent, is_up):
        font_family = '"Segoe UI", "Microsoft YaHei", sans-serif'
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 12)  # 顶部空间留给手柄区域
        main_layout.setSpacing(2)
        
        # 拖拽手柄层
        handle_layout = QHBoxLayout()
        handle_layout.addStretch()
        handle_layout.addWidget(self.drag_handle)
        handle_layout.addStretch()
        handle_layout.setContentsMargins(0, 0, 0, 0)
        
        # 头部布局
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 2, 0, 4)
        
        # 股票名称
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: #a6a6a6;
            font-family: {font_family};
            font-size: 13px;
            font-weight: bold;
        """)
        
        # 股票代码
        code_label = QLabel(code)
        code_label.setStyleSheet(f"""
            color: #555;
            font-family: {font_family};
            font-size: 11px;
        """)
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(code_label)
        
        # 主体布局
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(6)
        
        # 价格 - 处理过长价格的显示
        display_price = self.format_price(price)
        price_label = QLabel(display_price)
        price_label.setStyleSheet(f"""
            color: #ffffff;
            font-family: {font_family};
            font-size: 16px;
            font-weight: 600;
            max-width: 80px;
        """)
        price_label.setWordWrap(False)
        
        # 涨跌幅
        percent_label = QLabel(percent)
        bg = 'rgba(255, 77, 79, 0.1)' if is_up else 'rgba(82, 196, 26, 0.1)'
        fg = '#ff4d4f' if is_up else '#52c41a'
        
        percent_label.setStyleSheet(f"""
            color: {fg};
            background-color: {bg};
            font-family: {font_family};
            font-size: 11px;
            font-weight: 600;
            padding: 2px 4px;
            border-radius: 3px;
        """)
        percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        body_layout.addWidget(price_label)
        body_layout.addStretch()
        body_layout.addWidget(percent_label)
        
        # 组合所有层
        main_layout.addLayout(handle_layout)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(body_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式 - 模拟毛玻璃 (深色)
        self.setStyleSheet("""
            FloatCardWidget {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)
        
        # 添加更柔和的阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        # 固定大小 - 增加宽度以容纳更长的价格
        self.setFixedSize(150, 85)
        
    def setup_window_flags(self):
        """设置窗口标志"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def enterEvent(self, event):
        """鼠标进入时显示拖拽手柄"""
        self.drag_handle.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开时隐藏拖拽手柄"""
        self.drag_handle.hide()
        super().leaveEvent(event)
        
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