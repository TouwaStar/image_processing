
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TopMenu():
    def __init__(self, main_window, ):
        self.main_window = main_window
        self.main_menu = self.main_window.menuBar()

        self.file_menu = self.main_menu.addMenu('&File')
        self.operations_menu = self.main_menu.addMenu('&Operations')
        self.operations_thresholding_menu = self.operations_menu.addMenu('&Thresholding')

    def initialize_open_file(self, open_file_method):
        open_file = QAction("&Open File", self.main_window)
        open_file.setStatusTip('Open Image File')
        open_file.triggered.connect(open_file_method)

        self.file_menu.addAction(open_file)

    def initialize_negate(self, negate_method):
        negation = QAction("&Negate", self.main_window)
        negation.setStatusTip('Negate Image')
        negation.triggered.connect(negate_method)

        self.operations_menu.addAction(negation)

    def initialize_thresholding(self, thresholding_method, thresholding_variants: dict):
        for thresholding_variant in thresholding_variants:
            thresholding = QAction(f"&{thresholding_variant}", self.operations_thresholding_menu)
            thresholding.triggered.connect(lambda: thresholding_method(thresholding_variants[thresholding_variant]))
            self.operations_thresholding_menu.addAction(thresholding)

