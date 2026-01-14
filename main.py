import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window.main_window import ModernMainWindow


def main():
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("MarketEye")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MarketEye")
    
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # 禁止最后一个窗口关闭时退出程序（为了支持系统托盘）
    app.setQuitOnLastWindowClosed(False)
    
    # 创建并显示主窗口
    main_window = ModernMainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()