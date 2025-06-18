# main.py

import sys
from PyQt5.QtWidgets import QApplication
from view import MyWindow
from processor import PDFProcessor

if __name__ == "__main__":
    app = QApplication(sys.argv)

    processor = PDFProcessor()
    myWindow = MyWindow(processor)

    myWindow.show()
    app.exec_()
