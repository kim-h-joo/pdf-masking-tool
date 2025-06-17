import os
import datetime
from PIL import Image, ImageDraw, ImageFilter
import fitz


class PDFProcessor:
    def __init__(self):
        self.pdf_doc = None
        self.first_page = None
        self.rotation_degree = 0
        self.images = []

    def get_first_page(self):
        return self.first_page


    def try_open_pdf(self, file_path):
        try:
            self.pdf_doc = fitz.open(file_path)
            self.first_page = self.pdf_doc[0]
            self.rotation_degree = 0
            return True, None
        except Exception as e:
            return False, str(e)

    def page_to_fpix(self, page):
        fpix = page.get_pixmap(matrix=fitz.Matrix(1, 1).prerotate(self.rotation_degree))
        return fpix
    
    def change_degree(self, direction):
        if direction == -1:
            self.rotation_degree -= 90 # 반시계 방향 (왼쪽)
        elif direction == 1:
            self.rotation_degree += 90 # 시계 방향 (오른쪽)

    def make_img_list(self):
        for i, page in enumerate(self.pdf_doc):
            pixmap = self.page_to_fpix(page)
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            self.images.append(img)

def set_blur_region(self):
    pass

def blur_img(self):
    pass