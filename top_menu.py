
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from functools import partial

class TopMenu():
    """Defines the available operations and options in the top menu of the GUI
    every initialization creates a link to provided method that activates on mouse click"""
    def __init__(self, main_window, ):
        self.main_window = main_window
        self.main_menu = self.main_window.menuBar()

        self.file_menu = self.main_menu.addMenu('&File')
        self.operations_menu = self.main_menu.addMenu('&Operations')
        self.operations_thresholding_menu = self.operations_menu.addMenu('&Thresholding')
        self.operations_filtering_menu = self.operations_menu.addMenu('&Filtering')

        self.histogram_menu = self.main_menu.addMenu('&Histogram')

    def initialize_open_file(self, open_file_method):
        open_file = QAction("&Open File", self.main_window)
        open_file.setStatusTip('Open Image File')
        open_file.triggered.connect(open_file_method)

        self.file_menu.addAction(open_file)

    def initialize_save_file(self, save_file_method):
        save_file = QAction("&Save File", self.main_window)
        save_file.setStatusTip('Save Image File')
        save_file.triggered.connect(save_file_method)

        self.file_menu.addAction(save_file)

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

    def initialize_equalize_histogram(self, equalize_histogram):
        equalize = QAction("&Equalize Histogram", self.main_window)
        equalize.setStatusTip('Equalize Histogram')
        equalize.triggered.connect(equalize_histogram)

        self.operations_menu.addAction(equalize)

    def initialize_stretch_histogram(self, stretch_histogram):
        stretch = QAction("&Stretch Histogram", self.main_window)
        stretch.setStatusTip('Stretch Histogram')
        stretch.triggered.connect(stretch_histogram)

        self.operations_menu.addAction(stretch)

    def initialize_thresholding(self, thresholding_method, thresholding_variants: dict):
        for thresholding_variant in thresholding_variants:
            thresholding = QAction(f"&{thresholding_variant}", self.operations_thresholding_menu)
            print(thresholding_variant)
            print(thresholding_variants[thresholding_variant])
            thresholding.triggered.connect(partial(thresholding_method, thresholding_variants[thresholding_variant], None))
            self.operations_thresholding_menu.addAction(thresholding)



    def initialize_linear_filtering(self, linear_filtering_method):
        linear_filtering = QAction("&Linear Filtering", self.operations_filtering_menu)
        linear_filtering.setStatusTip('Liner Filtering')
        linear_filtering.triggered.connect(linear_filtering_method)

        self.operations_filtering_menu.addAction(linear_filtering)

    def initialize_morphology(self, morphology_method):
        morphology = QAction("&Morphology", self.operations_filtering_menu)
        morphology.setStatusTip('Morphology')
        morphology.triggered.connect(morphology_method)

        self.operations_filtering_menu.addAction(morphology)

    def initialize_segmentation(self, segmentation_method):
        segmentation = QAction("&Segmentation", self.operations_menu)
        segmentation.setStatusTip('Segmentation')
        segmentation.triggered.connect(segmentation_method)

        self.operations_menu.addAction(segmentation)

    def initialize_skeletize(self, skeletize_method):
        skeletize = QAction("&Skeletize", self.operations_menu)
        skeletize.setStatusTip('Skeletize')
        skeletize.triggered.connect(skeletize_method)

        self.operations_menu.addAction(skeletize)

    def initialize_fourier(self, fourier_method):
        fourier = QAction("&Fourier", self.operations_menu)
        fourier.setStatusTip('Fourier')
        fourier.triggered.connect(fourier_method)

        self.operations_menu.addAction(fourier)

    def initialize_shape_descriptors(self, moments_and_shapes_method):
        moments_and_shapes = QAction("&Moments and Shape Descriptors", self.operations_menu)
        moments_and_shapes.setStatusTip('Moments and Shape Descriptors')
        moments_and_shapes.triggered.connect(moments_and_shapes_method)

        self.operations_menu.addAction(moments_and_shapes)

    def initialize_histogram_options(self, histogram_method, histogram_variants: dict):
        for histogram_variant in histogram_variants:
            histogram = QAction(f"&{histogram_variant}", self.histogram_menu)
            print(histogram_variant)
            print(histogram_variants[histogram_variant])
            histogram.triggered.connect(partial(histogram_method, histogram_variants[histogram_variant]))
            self.histogram_menu.addAction(histogram)


