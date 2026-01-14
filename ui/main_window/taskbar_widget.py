"""
任务栏风格的主窗口组件
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QScreen, QGuiApplication


class StockItem(QWidget):
    """单个股票显示项"""
    
    def __init__(self, name, price, percent, is_up=True):
        super().__init__()
        self.init_ui(name, price, percent, is_up)
        
    def init_ui(self, name, price, percent, is_up):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(6)
        
        # 字体设置
        font_family = '"Segoe UI", "Microsoft YaHei", sans-serif'
        
        # 股票名称
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: #a6a6a6; font-family: {font_family}; font-size: 12px;")
        
        # 价格
        price_label = QLabel(price)
        price_label.setStyleSheet(f"""
            color: {'#ff4d4f' if is_up else '#52c41a'};
            font-family: {font_family};
            font-size: 13px;
            font-weight: 600;
        """)
        
        # 涨跌幅
        percent_label = QLabel(percent)
        percent_label.setStyleSheet(f"""
            color: {'#ff4d4f' if is_up else '#52c41a'};
            font-family: {font_family};
            font-size: 13px;
            font-weight: 600;
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(percent_label)
        
        self.setLayout(layout)
        
        # 移除悬停和点击特效，保持完全静态和透明
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)


class TaskbarWidget(QWidget):
    """任务栏吸附窗口"""
    
    def __init__(self):
        super().__init__()
        # 设置窗口标志：无边框 | 置顶 | 工具窗口(不在任务栏显示图标)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 支持透明背景
        
        # 内部布局引用
        self.content_layout = None
        
        self.init_ui()
        self.adjust_position()
        
    def init_ui(self):
        # 模拟任务栏背景色 (深色模式 #1e1e1e)
        self.setStyleSheet("""
            TaskbarWidget {
                background-color: #1e1e1e;
                border-top: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        
        self.setFixedHeight(32)  # 高度稍微减小以适应任务栏
        
        # 主布局
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 10, 0)
        self.content_layout.setSpacing(10)
        
        # 移除拖拽把手，改为纯静态展示
        # handle = QLabel("⋮")
        # handle.setStyleSheet("color: #666; font-weight: bold; cursor: move;")
        # self.content_layout.addWidget(handle)
        
        self.setLayout(self.content_layout)

    def update_stocks(self, stock_list):
        """
        更新显示的股票列表
        :param stock_list: [{"name": str, "price": str, "percent": str, "is_up": bool}, ...]
        """
        # 清除所有控件
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 添加新数据
        for i, stock in enumerate(stock_list):
            if i > 0:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.VLine)
                divider.setStyleSheet("background-color: #444; max-width: 1px; max-height: 14px;")
                self.content_layout.addWidget(divider)
            
            stock_item = StockItem(
                stock['name'], 
                stock['price'], 
                stock['percent'], 
                stock['is_up']
            )
            self.content_layout.addWidget(stock_item)
            
        self.adjustSize()
        self.adjust_position()

    def adjust_position(self):
        """自动吸附到主屏幕底部居中位置"""
        screen = QGuiApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            # 定位到底部，水平居中 (稍微往上一点点，避免完全遮挡底部线条)
            x = geometry.x() + (geometry.width() - self.sizeHint().width()) // 2
            y = geometry.height() - self.height() 
            self.move(x, y)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_start_position') and event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + diff)
            self.drag_start_position = event.globalPosition().toPoint()