
import cv2
import logging as log

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class ImageWindow():
    def __init__(self, main_window):
        self.main_window = main_window
        self._original_image = None
        self.cv_image = None
        self.mq_image = None

        contents = QLabel()
        contents.setFixedSize(400, 400)

        contents.setStyleSheet("background-color: white; border: 2px inset grey;")
        contents.setScaledContents(True)

        self.image = contents



    def set_image_from_file(self):
        try:
            fname = QFileDialog.getOpenFileName(self.main_window, 'Open file',
                                                'c:\\', "Image files (*.jpg *.gif)")[0]

            print("Opening " + fname)
            self.cv_image = cv2.imread(fname)
            self._original_image = self.cv_image
            self._set_image()
        except Exception as e:
            log.error(repr(e))

    def _set_image(self):
        try:

            height, width, byteValue = self.cv_image.shape
            byteValue = byteValue * width

            cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB, self.cv_image)
            self.mq_image = QImage(self.cv_image, width, height, byteValue, QImage.Format_RGB888)


            aspect_ratio = width/height
            self.image.setFixedSize(400 * aspect_ratio, 400)
            self.image.setPixmap(QPixmap.fromImage(self.mq_image))

            self.main_window.histogram_window.set_histogram(self.cv_image)
        except Exception as e:
            log.error(repr(e))

    def negate_image(self):
        self.cv_image = cv2.bitwise_not(self.cv_image)
        self._set_image()

    def threshold_image(self, type):
        ret, self.cv_image = cv2.threshold(self.cv_image,127,255, type)
        self._set_image()



