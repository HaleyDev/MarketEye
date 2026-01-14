"""
现代化的主控制面板
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QListWidget, QListWidgetItem, QStackedWidget, 
                             QMessageBox, QFrame, QScrollArea, QApplication,
                             QGraphicsDropShadowEffect, QGridLayout, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction, QColor, QPixmap, QPainter, QPen
import sys

from ..main_window.taskbar_widget import TaskbarWidget
from ..widgets.float_ime_widget import FloatIMEWidget
from ..widgets.float_card_widget import FloatCardWidget
from data.providers.stock_provider import StockProvider


class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.stocks_config = []  # 存储配置
        self.active_widgets = [] # 存储当前活动的悬浮窗实例
        self.taskbar_widget_instance = None # 任务栏组件实例
        
        self.init_ui()
        self.create_tray_icon()
        
    def create_tray_icon(self):
        """创建系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 绘制一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 画一个蓝色背景圆
        painter.setBrush(QColor("#409eff"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        
        # 画一个M字母
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        # M shape
        # 8,10 -> 8,22
        painter.drawLine(8, 10, 8, 22)
        # 8,10 -> 16,16
        painter.drawLine(8, 10, 16, 16)
        # 16,16 -> 24,10
        painter.drawLine(16, 16, 24, 10)
        # 24,10 -> 24,22
        painter.drawLine(24, 10, 24, 22)
        
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("MarketEye - 看盘助手")
        
        # 创建菜单
        menu = QMenu()
        
        action_show = QAction("显示设置面板", self)
        action_show.triggered.connect(self.show_window)
        
        action_quit = QAction("退出程序", self)
        action_quit.triggered.connect(self.quit_app)
        
        menu.addAction(action_show)
        menu.addSeparator()
        menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
    def show_window(self):
        self.show()
        self.activateWindow()
        self.raise_()
        
    def quit_app(self):
        # 关闭所有窗口
        if self.taskbar_widget_instance:
            self.taskbar_widget_instance.close()
        for w in self.active_widgets:
            w.close()
        QApplication.quit()
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def create_nav_icon(self, shape_type):
        """创建包含普通和选中状态的矢量图标"""
        def draw_shape(painter, color):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            
            if shape_type == "dashboard":
                # 绘制4个圆角矩形组成的网格
                size = 20
                box = 8
                gap = 4
                painter.drawRoundedRect(0, 0, box, box, 2, 2)
                painter.drawRoundedRect(box + gap, 0, box, box, 2, 2)
                painter.drawRoundedRect(0, box + gap, box, box, 2, 2)
                painter.drawRoundedRect(box + gap, box + gap, box, box, 2, 2)
                
            elif shape_type == "about":
                # 绘制info图标
                painter.setPen(QPen(QColor(color), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(1, 1, 18, 18)
                
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(color))
                painter.drawEllipse(9, 5, 2, 2)
                painter.drawRoundedRect(9, 9, 2, 6, 1, 1)

        # 颜色定义
        color_normal = "#909399"  # 灰色
        color_active = "#409eff"  # 蓝色
        
        # 创建图标对象
        icon = QIcon()
        
        # 1. 普通状态
        pix_normal = QPixmap(20, 20)
        pix_normal.fill(Qt.GlobalColor.transparent)
        p_normal = QPainter(pix_normal)
        p_normal.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_shape(p_normal, color_normal)
        p_normal.end()
        icon.addPixmap(pix_normal, QIcon.Mode.Normal, QIcon.State.Off)
        
        # 2. 选中状态 (利用 QListWidget 的特性，选中时通常会高亮)
        # 注意：QListWidget 默认不像 Button 那样自动切换 Icon Mode，
        # 但我们可以通过 Selected 状态来自动处理，或者仅仅依靠背景色变化。
        # 为了效果最好，我们还是生成一个，虽然 QListWidget 可能不自动切换图标颜色，
        # 除非我们重写 paint 或者用 stylesheet 设置图标（stylesheet 不支持动态生成的图标）。
        # 最简单的增强是：我们只提供灰色图标，但是因为背景变蓝，对比度还可以。
        # 或者我们直接生成蓝色图标。
        
        # 实际上 QIcon 在 QListWidget item 被 select 时不会自动变成 Selected Mode，
        # 除非我们自定义 delegate。
        # 这里为了简单且好看，我们用稍微深一点的灰色或者品牌色作为默认图标。
        # 如果想让它看起来更“高级”，就用前面定义的深灰色 #5e6d82。
        
        return icon

    def init_ui(self):
        self.setWindowTitle('MarketEye 设置')
        self.setFixedSize(800, 600)
        
        # 主容器
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        # 字体
        self.font_main = "Segoe UI"
        self.font_cn = "Microsoft YaHei"
        
        # 全局样式优化
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #f5f7fa; }}
            QWidget {{ font-family: "{self.font_main}", "{self.font_cn}"; }}
            
            /* 侧边栏 */
            QListWidget {{
                background-color: #ffffff;
                border: none;
                outline: none;
                padding-top: 20px;
            }}
            QListWidget::item {{
                height: 52px; /* 增加高度 */
                padding-left: 10px; /* 减小一点，因为有图标了 */
                color: #5e6d82;
                border-left: 4px solid transparent;
                margin-bottom: 8px; /* 增加间距 */
                border-radius: 0 26px 26px 0; /* 右侧圆角 */
                margin-right: 16px;
            }}
            QListWidget::item:selected {{
                background-color: #ecf5ff;
                color: #409eff;
                border-left-color: transparent; /* 取消左侧边框模式，改用全背景 */
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: #f5f7fa;
            }}
            
            /* 通用标签 */
            QLabel {{ color: #606266; }}
            
            /* 输入框及下拉框 - 修复字体颜色 */
            QLineEdit, QComboBox {{
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 0 12px;
                height: 36px;
                background: #ffffff;
                color: #333333; /* 强制深色字体 */
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: #409eff;
            }}
            QLineEdit::placeholder {{
                color: #c0c4cc;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            /* 卡片容器 */
            .Card {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ebeef5;
            }}
        """)
        
        # 主布局：左侧导航 + 右侧内容
        layout = QHBoxLayout(main_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧导航栏容器 (加阴影)
        nav_container = QWidget()
        nav_container.setFixedWidth(220) # 稍微加宽
        nav_container.setStyleSheet("background-color: white; border-right: 1px solid #e6e6e6;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # Logo 区域
        logo_label = QLabel("MarketEye")
        logo_label.setFixedHeight(70)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet(f"font-family: 'Segoe UI Black', 'Arial Black'; font-size: 24px; color: #303133; border-bottom: 1px solid #f0f0f0;")
        nav_layout.addWidget(logo_label)
        
        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.setIconSize(QSize(20, 20)) # 设置图标大小
        
        item_manage = QListWidgetItem(self.create_nav_icon("dashboard"), "  股票配置")
        self.nav_list.addItem(item_manage)
        
        item_about = QListWidgetItem(self.create_nav_icon("about"), "  关于软件")
        self.nav_list.addItem(item_about)
        
        self.nav_list.currentRowChanged.connect(self.switch_page)
        nav_layout.addWidget(self.nav_list)
        
        # 右侧内容区
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.create_manage_page())
        self.content_stack.addWidget(self.create_about_page())
        
        layout.addWidget(nav_container)
        layout.addWidget(self.content_stack)
        
        # 默认选中第一页
        self.nav_list.setCurrentRow(0)
        
    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        
    def create_card_effect(self, widget):
        """给 Widget 添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)
        
    def create_manage_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # 顶部标题栏
        header_layout = QHBoxLayout()
        title = QLabel("自选股配置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #303133;")
        
        # 应用按钮放在右上角
        btn_apply = QPushButton("🚀 应用/刷新")
        btn_apply.setFixedSize(120, 36)
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #67c23a;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #85ce61; }
            QPushButton:pressed { background-color: #5daf34; }
        """)
        btn_apply.clicked.connect(self.refresh_display)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_apply)
        layout.addLayout(header_layout)
        
        # --- 添加股票卡片 ---
        add_card = QWidget()
        add_card.setProperty("class", "Card")
        self.create_card_effect(add_card)
        add_layout = QVBoxLayout(add_card)
        add_layout.setContentsMargins(25, 25, 25, 25)
        add_layout.setSpacing(15)
        
        add_title = QLabel("添加新股票")
        add_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #303133; margin-bottom: 5px;")
        add_layout.addWidget(add_title)
        
        # Grid 布局表单
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1) # 让第二列填满
        
        # Row 1: 代码
        form_layout.addWidget(QLabel("股票代码"), 0, 0)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("例如: sh600519 或 sz000001 (Mock模式下任意输入)")
        form_layout.addWidget(self.input_code, 0, 1)
        
        # Row 2: 名称
        form_layout.addWidget(QLabel("显示名称"), 1, 0)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("例如: 茅台 (用于界面展示)")
        form_layout.addWidget(self.input_name, 1, 1)
        
        # Row 3: 类型
        form_layout.addWidget(QLabel("展示样式"), 2, 0)
        self.combo_type = QComboBox()
        self.combo_type.addItems(["🖥️  任务栏嵌入模式", "📏  桌面悬浮 (条形)", "🗂️  桌面悬浮 (卡片)"])
        form_layout.addWidget(self.combo_type, 2, 1)
        
        add_layout.addLayout(form_layout)
        
        # 添加按钮居右
        btn_add = QPushButton("＋ 添加到列表")
        btn_add.setFixedSize(120, 36)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #66b1ff; }
            QPushButton:pressed { background-color: #3a8ee6; }
        """)
        btn_add.clicked.connect(self.add_stock)
        add_layout.addWidget(btn_add, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(add_card)
        
        # --- 列表区域 ---
        list_header_layout = QHBoxLayout()
        list_title = QLabel("已配置列表")
        list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #303133;")
        self.limit_label = QLabel("0/4")
        self.limit_label.setStyleSheet("background-color: #e6a23c; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px;")
        
        list_header_layout.addWidget(list_title)
        list_header_layout.addWidget(self.limit_label)
        list_header_layout.addStretch()
        
        layout.addLayout(list_header_layout)
        
        # 滚动区域容器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        self.list_layout = QVBoxLayout(scroll_content)
        self.list_layout.setContentsMargins(0, 0, 5, 0) # 右侧留点空隙给滚动条
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch() # 顶部对齐
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        return page
        
    def create_stock_item_widget(self, index, config):
        """创建列表项的小卡片"""
        item_widget = QWidget()
        item_widget.setFixedHeight(70)
        item_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #ebeef5;
            }
            QWidget:hover {
                border-color: #c6e2ff;
                background-color: #fcfdfe;
            }
        """)
        
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # 图标/序号
        idx_label = QLabel(str(index + 1))
        idx_label.setFixedSize(24, 24)
        idx_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idx_label.setStyleSheet("background-color: #f0f2f5; color: #909399; border-radius: 12px; font-weight: bold; border: none;")
        
        # 信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        name_label = QLabel(f"{config['name']}  <span style='color:#909399; font-size:12px;'>{config['code']}</span>")
        name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #303133; border: none; background: transparent;")
        
        # 类型标签颜色
        type_colors = {
            "taskbar": "#909399", # 灰
            "ime": "#e6a23c",     # 黄
            "card": "#409eff"     # 蓝
        }
        color = type_colors.get(config['type'], "#909399")
        type_label = QLabel(config['type_display'])
        type_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 500; border: none; background: transparent;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(type_label)
        
        # 删除按钮
        btn_del = QPushButton("×")
        btn_del.setFixedSize(30, 30)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("删除")
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f56c6c;
                font-size: 20px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #fef0f0; }
        """)
        btn_del.clicked.connect(lambda: self.remove_stock(index))
        
        layout.addWidget(idx_label)
        layout.addSpacing(15)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(btn_del)
        
        return item_widget

    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 卡片容器
        card = QWidget()
        card.setProperty("class", "Card")
        self.create_card_effect(card)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        title = QLabel("MarketEye")
        title.setStyleSheet("font-size: 32px; font-weight: 900; color: #303133;")
        
        subtitle = QLabel("轻量级桌面看盘助手")
        subtitle.setStyleSheet("font-size: 16px; color: #909399; margin-bottom: 20px;")
        
        desc = QLabel(
            "<p style='line-height:1.6'><b>MarketEye</b> 旨在提供无干扰的行情关注体验。通过任务栏嵌入和桌面悬浮窗，让您在工作之余随时掌握市场动态。</p>"
            "<hr style='margin: 15px 0; border: none; border-top: 1px solid #eee;'>"
            "<p><b>Version:</b> 1.0.0 (Beta)</p>"
            "<p><b>License:</b> MIT Open Source</p>"
            "<br>"
            "<p style='color:#909399; font-size: 12px;'>* 本程序当前使用随机 Mock 数据，请在源码 `data/providers/stock_provider.py` 中接入您的 API。</p>"
        )
        desc.setStyleSheet("font-size: 14px; color: #606266;")
        desc.setWordWrap(True)
        
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(desc)
        card_layout.addStretch()
        
        layout.addWidget(card)
        layout.addStretch()
        
        return page

    def add_stock(self):
        code = self.input_code.text().strip()
        name = self.input_name.text().strip()
        type_idx = self.combo_type.currentIndex()
        
        # 映射类型
        type_map = {0: "taskbar", 1: "ime", 2: "card"}
        type_str = type_map.get(type_idx, "taskbar")
        type_name_map = {0: "任务栏嵌入", 1: "桌面悬浮 (条形)", 2: "桌面悬浮 (卡片)"}
        
        if not code or not name:
            QMessageBox.warning(self, "提示", "请填写完整的股票代码和名称")
            return
            
        if len(self.stocks_config) >= 4:
            QMessageBox.warning(self, "提示", "最多支持添加 4 个自选股")
            return
            
        # 添加配置
        config = {"code": code, "name": name, "type": type_str, "type_display": type_name_map[type_idx]}
        self.stocks_config.append(config)
        
        # 更新列表UI
        self.update_list_ui()
        
        # 清空输入
        self.input_code.clear()
        self.input_name.clear()
        
    def update_list_ui(self):
        # 清空现有列表 (保留最后一个 stretch item)
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 重新填充
        for idx, config in enumerate(self.stocks_config):
            item_widget = self.create_stock_item_widget(idx, config)
            self.list_layout.insertWidget(idx, item_widget)
            
        # 更新计数文字
        count = len(self.stocks_config)
        self.limit_label.setText(f"{count}/4")
        if count >= 4:
            self.limit_label.setStyleSheet("background-color: #f56c6c; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px;")
        else:
            self.limit_label.setStyleSheet("background-color: #e6a23c; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px;")
            
    def remove_stock(self, index):
        if 0 <= index < len(self.stocks_config):
            self.stocks_config.pop(index)
            self.update_list_ui()
            
    def refresh_display(self):
        """核心逻辑：根据配置重新生成所有展示窗口"""
        
        # 1. 也是清理旧窗口
        if self.taskbar_widget_instance:
            self.taskbar_widget_instance.close()
            self.taskbar_widget_instance = None
            
        for w in self.active_widgets:
            w.close()
        self.active_widgets.clear()
        
        # 2. 分类处理配置
        taskbar_stocks = []
        
        # 获取数据 (Mock)
        for config in self.stocks_config:
            # 获取数据
            data = StockProvider.get_stock_data(config['code'])
            # 组合显示名称
            display_name = config['name']
            
            if config['type'] == 'taskbar':
                taskbar_info = data.copy()
                taskbar_info['name'] = display_name
                taskbar_stocks.append(taskbar_info)
                
            elif config['type'] == 'ime':
                # 创建 IME 悬浮窗
                w = FloatIMEWidget(display_name, data['price'], data['percent'], data['is_up'])
                # 简单排布位置，防止重叠
                count = len(self.active_widgets)
                w.move(100, 200 + count * 50)
                w.show()
                self.active_widgets.append(w)
                
            elif config['type'] == 'card':
                # 创建卡片悬浮窗
                w = FloatCardWidget(display_name, config['code'].upper(), data['price'], data['percent'], data['is_up'])
                # 简单排布
                total_float = len(self.active_widgets)
                w.move(400 + (total_float%2)*140, 200 + (total_float//2)*100)
                w.show()
                self.active_widgets.append(w)
        
        # 3. 统一处理任务栏
        if taskbar_stocks:
            self.taskbar_widget_instance = TaskbarWidget()
            self.taskbar_widget_instance.update_stocks(taskbar_stocks)
            self.taskbar_widget_instance.show()
            
        QMessageBox.information(self, "成功", "展示已更新！\n数据为MOCK模拟数据，请知悉。")

    def closeEvent(self, event):
        # 最小化到托盘而不是直接退出
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "MarketEye",
                "程序已最小化到系统托盘，双击图标可重新打开设置面板。",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()