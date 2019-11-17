
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from functools import partial

class TopMenu():
    def __init__(self, main_window, ):
        self.main_window = main_window
        self.main_menu = self.main_window.menuBar()

        self.file_menu = self.main_menu.addMenu('&File')
        self.operations_menu = self.main_menu.addMenu('&Operations')
        self.operations_thresholding_menu = self.operations_menu.addMenu('&Thresholding')

        self.histogram_menu = self.main_menu.addMenu('&Histogram')

    def initialize_open_file(self, open_file_method):
        open_file = QAction("&Open File", self.main_window)
        open_file.setStatusTip('Open Image File')
        open_file.triggered.connect(open_file_method)

        self.file_menu.addAction(open_file)

    def initialize_grayscale_conversion(self, convert_method):
        convert_to_gray = QAction("&Convert to Grayscale", self.main_window)
        convert_to_gray.setStatusTip('Convert to Grayscale')
        convert_to_gray.triggered.connect(convert_method)

        self.file_menu.addAction(convert_to_gray)

    def initialize_reset_image(self, reset_image_method):
        reset_image = QAction("&Reset Image", self.main_window)
        reset_image.setStatusTip('Reset Image')
        reset_image.triggered.connect(reset_image_method)

        self.file_menu.addAction(reset_image)

    def initialize_negate(self, negate_method):
        negation = QAction("&Negate", self.main_window)
        negation.setStatusTip('Negate Image')
        negation.triggered.connect(negate_method)

        self.operations_menu.addAction(negation)

    def initialize_thresholding(self, thresholding_method, thresholding_variants: dict):
        for thresholding_variant in thresholding_variants:
            thresholding = QAction(f"&{thresholding_variant}", self.operations_thresholding_menu)
            print(thresholding_variant)
            print(thresholding_variants[thresholding_variant])
            thresholding.triggered.connect(partial(thresholding_method, thresholding_variants[thresholding_variant]))
            self.operations_thresholding_menu.addAction(thresholding)

    def initialize_histogram_options(self, histogram_method, histogram_variants: dict):
        for histogram_variant in histogram_variants:
            histogram = QAction(f"&{histogram_variant}", self.histogram_menu)
            print(histogram_variant)
            print(histogram_variants[histogram_variant])
            histogram.triggered.connect(partial(histogram_method, histogram_variants[histogram_variant]))
            self.histogram_menu.addAction(histogram)

