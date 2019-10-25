import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import logging as log
import cv2

from consts import THRESHOLDINGS
from image_window import ImageWindow
from histogram_window import HistogramWindow
from top_menu import TopMenu

class APO_app(QMainWindow):
    def __init__(self, parent=None):
        super(APO_app, self).__init__(parent)
        self.setMinimumSize(800, 400)

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
        self.top_menu.initialize_negate(self.image_window.negate_image)

        self.top_menu.initialize_thresholding(self.image_window.threshold_image,THRESHOLDINGS)

        self.setWindowTitle("Project Apo")







def main():
    try:
        app = QApplication(sys.argv)
        ex = APO_app()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        log.error(repr(e))


if __name__ == '__main__':
    main()