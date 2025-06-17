import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
import getpass
import fitz
from PIL import Image, ImageFilter, ImageDraw
import datetime


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("main.ui")
form_class = uic.loadUiType(form)[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('PDF2IMG')
        self.setWindowIcon(QIcon(resource_path('icon.png')))

        self.pdf_file = None
        self.first_page = None
        self.rotation_degree = 0
        self.images = []
        self.save_dir_path = ""
        self.user_name = getpass.getuser()

        # 파일 선택
        self.openBT.clicked.connect(self.openFile)
        # 왼쪽 90도 회전
        self.rotateBT_L.clicked.connect(self.rotateL)
        # 오른쪽 90도 회전
        self.rotateBT_R.clicked.connect(self.rotateR)
        # 변환
        self.convertBT.clicked.connect(self.convert)

    #------------------------------------------------------------#
    def openFile(self):
        self.stateLabel.setText("")
        dir_path = os.path.join("C:\\Users", self.user_name, "Downloads")
        file_name, _ = QFileDialog.getOpenFileName(self, '파일 선택', dir_path, 'PDF Files (*.pdf)')
        self.name = file_name
        if file_name:
            self.load_pdf(file_name)
            self.display_page()
            self.nameView.setText(os.path.basename(file_name))
            self.images = []

    def load_pdf(self, file_name):
        self.pdf_file = fitz.open(file_name)
        self.first_page = self.pdf_file[0]
        self.rotation_degree = 0

    def display_page(self):
        # pdf -> pixmap
        if self.first_page is not None:
            page = self.first_page
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1).prerotate(self.rotation_degree))
            # -> PyMuPDF pixmap

            image = QPixmap()
            image.loadFromData(pixmap.tobytes("ppm"))
            # pixmap -> QPixmap 객체로 변환 (PyQt용 UI 이미지로 변환)

            # scene = QGraphicsScene(self)
            # item = QGraphicsPixmapItem(image)
            # scene.addItem(item)
            # self.graphicsView.setScene(scene)
            # self.graphicsView.fitInView(item, Qt.KeepAspectRatio)

    def rotateL(self):
        self.rotation_degree -= 90
        self.display_page()

    def rotateR(self):
        self.rotation_degree += 90
        self.display_page()


    def convert(self):
        self.stateLabel.setText("진행 중")

        self.convert_to_png()

        if(self.userListBT.isChecked()):
            self.img_blur()
            self.makeSaveDir()
            self.create_image_grid()

        elif(self.makingListBT.isChecked()):
            self.img_blur((227,216), (510,713))
            self.makeSaveDir('공작소')
            self.create_image_grid(2,2)
        else:
            self.msg_box("error::conversion type not selected")
            sys.exit(1)

        self.stateLabel.setText("완료")
        self.openDir()


    def convert_to_png(self):
        if self.pdf_file is not None:
            for i, page in enumerate(self.pdf_file):
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1).prerotate(self.rotation_degree))
                img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                self.images.append(img)

    def img_blur(self, point_1=(100, 208), point_2=(183, 495)):
        top_left = point_1
        bottom_right = point_2
        img_width, img_height = self.images[0].size
        aspect_ratio = img_height / img_width
        new_width = 1240
        new_height = int(1240 * aspect_ratio)

        for i in range(len(self.images)):
            img = self.images[i]
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([top_left, bottom_right], fill=255)
            blurred_region = img.filter(ImageFilter.GaussianBlur(radius=5))
            img.paste(blurred_region, mask=mask)
            self.images[i] = img.resize((new_width, new_height))

    def create_image_grid(self, rows=4, cols=2):
        if not self.images:
            self.msg_box("error::images list empty")
            sys.exit(1)

        # 이미지 크기 가져오기
        img_width, img_height = self.images[0].size

        # 이미지 수에 따라 필요한 페이지 수 계산
        total_images = len(self.images)
        images_per_page = rows * cols
        num_pages = (total_images + images_per_page - 1) // images_per_page  # 올림 계산

        for page_num in range(num_pages):
            # 페이지당 이미지 인덱스 계산
            start_index = page_num * images_per_page
            end_index = min(start_index + images_per_page, total_images)
            page_images = self.images[start_index:end_index]

            # 페이지 이미지 크기 계산
            grid_width = img_width * cols
            grid_height = img_height * rows

            # 그리드 이미지를 새로 생성
            grid_image = Image.new('RGB', (grid_width, grid_height), color='white')

            # 이미지 그리드에 이미지를 붙여넣기
            for index, img in enumerate(page_images):
                row = index // cols
                col = index % cols
                # 계산된 위치에 이미지 붙여넣기
                grid_image.paste(img, (col * img_width, row * img_height))

            # 페이지별 그리드 이미지 저장
            grid_image.save(os.path.join(self.save_dir_path, (str(page_num + 1) + ".png")))


    def makeSaveDir(self, typeofList='이용대장'):
        rootPath = os.path.join("C:\\Users", self.user_name, "Desktop", "PDF2IMG")
        if not os.path.exists(rootPath):
            os.makedirs(rootPath)
        date = datetime.datetime.now()
        self.save_dir_path = os.path.join(rootPath, f"{date.strftime('%Y-%m')}_{typeofList}")
        if not os.path.exists(self.save_dir_path):
            os.mkdir(self.save_dir_path)
        else:
            self.msg_box("error::directory already exists")
            sys.exit(1)

    def openDir(self):
        os.startfile(self.save_dir_path)

    def msg_box(self, text):
        msg = QMessageBox()
        msg.setWindowTitle(" ")
        msg.setText(text)
        msg.exec_()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
