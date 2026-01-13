import sys
# 使用 PyQt5
from PyQt5.QtWidgets import QApplication, QLabel
# 或使用 PySide6
# from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel('Hello, MarketEye!')
label.show()
sys.exit(app.exec_())