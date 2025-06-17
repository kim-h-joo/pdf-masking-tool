import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt


def resource_path(relative_path):
    """ 리소스 파일 절대 경로 반환 함수, PyInstaller 오류 방지용 """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("main.ui")
form_class = uic.loadUiType(form)[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self, processor):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.processor = processor

    def init_ui(self):
        self.setWindowTitle('PDF2IMG')
        self.setWindowIcon(QIcon(resource_path('icon.png')))
        self.stateLabel.setText("")

    def connect_signals(self):
        # 파일 선택
        self.openBT.clicked.connect(self.load_file())
        # 왼쪽 90도 회전
        self.rotateBT_L.clicked.connect(self.rotate_left())
        # 오른쪽 90도 회전
        self.rotateBT_R.clicked.connect(self.rotate_right())
        # 변환
        self.convertBT.clicked.connect(self.convert)

    def msg_box(self, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(" ")
        msg.setText(text)
        msg.exec_()

    def display_pixmap(self, page):
        pixmap = self.processor.page_to_fpix(page)
        qpixmap = QPixmap()
        qpixmap.loadFromData(pixmap.tobytes("ppm"))
        # if not qpixmap.loadFromData(pixmap.tobytes("ppm")):
        #     self.msg_box("이미지를 로드할 수 없습니다.")
        #     return
        qscene = QGraphicsScene(self)
        qitem = QGraphicsPixmapItem(qpixmap)
        qscene.addItem(qitem)
        self.graphicsView.setScene(qscene)
        self.graphicsView.fitInView(qitem, Qt.KeepAspectRatio)


    def load_file(self):
        dir_path = str(Path.home() / "Downloads")
        file_path, _ = QFileDialog.getOpenFileName(self, 'PDF 파일 선택', dir_path, 'PDF Files (*.pdf)')
        if not file_path:
            return
        
        is_success, err_msg = self.processor.try_open_pdf(file_path)
        if not is_success:
            self.msg_box(err_msg)
            return
        self.nameView.setText(os.path.basename(file_path))
        self.display_pixmap(self.processor.get_first_page())

    def rotate_left(self):
        self.processor.change_degree(-1)
        self.display_pixmap(self.processor.get_first_page())

    def rotate_right(self):
        self.processor.change_degree(1)
        self.display_pixmap(self.processor.get_first_page())
