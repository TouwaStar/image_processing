import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import logging as log
import cv2

from consts import THRESHOLDINGS, HISTOGRAMS
from image_window import ImageWindow
from histogram_window import HistogramWindow
from top_menu import TopMenu

class APO_app(QMainWindow):
    """Main class of the applications, contains all the high level logic and initializes all the components"""
    def __init__(self, parent=None):
        super(APO_app, self).__init__(parent)
        self.setMinimumSize(1200, 400)

        self._main = QWidget()

        self.setCentralWidget(self._main)

        layout = QGridLayout(self._main)

        self.image_window = ImageWindow(self)
        self.histogram_window = HistogramWindow(self)
        layout.addWidget(self.image_window.image, 1, 0)
        layout.addWidget(self.histogram_window.image, 1, 1)


        self.setLayout(layout)

        self.top_menu = TopMenu(self)
        self.top_menu.initialize_open_file(self.image_window.set_image_from_file)
        self.top_menu.initialize_save_file(self.image_window.save_image_to_file)
        self.top_menu.initialize_reset_image(self.image_window.reset_image)
        self.top_menu.initialize_grayscale_conversion(self.image_window.change_to_grayscale)

        self.top_menu.initialize_negate(self.image_window.negate_image)
        self.top_menu.initialize_equalize_histogram(self.image_window.equalize_histogram)
        self.top_menu.initialize_stretch_histogram(self.image_window.stretch_histogram)
        self.top_menu.initialize_skeletize(self.image_window.skeletize)

        self.top_menu.initialize_thresholding(self.image_window.threshold_image, THRESHOLDINGS)

        self.top_menu.initialize_linear_filtering(self.image_window.linear_filtering)
        self.top_menu.initialize_morphology(self.image_window.morphological_operations)
        self.top_menu.initialize_segmentation(self.image_window.segmentation_operations)
        self.top_menu.initialize_shape_descriptors(self.image_window.shape_descriptors_operations)
        self.top_menu.initialize_fourier(self.image_window.fourier)


        self.top_menu.initialize_histogram_options(self.image_window.set_histogram, HISTOGRAMS)


        self.setWindowTitle("Project Apo")

def main():
    """Runs our application

    2 z 3cich jest zle
    3cie z 3cich tylko konkretne kierunki

    do pokazania poprawione juz
    """
    try:
        app = QApplication(sys.argv)
        ex = APO_app()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(repr(e))


if __name__ == '__main__':
    main()