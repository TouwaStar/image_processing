import cv2
import logging as log

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
from numpy import arange, sin, pi
from consts import HISTOGRAM_TYPES


class HistogramWindow():
    def __init__(self, main_window):
        self.main_window = main_window
        self.cv_image = None
        self.mq_image = None

        contents = QWidget()
        contents.setMaximumSize(600, 400)

        contents.setStyleSheet("background-color: white; border: 2px inset grey;")

        self.image = contents

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, main_window)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.image.setLayout(layout)

        self.last_histogram_type = HISTOGRAM_TYPES.Bar

    def set_histogram(self, image, type=None):
        try:
            if not type:
                type_to_set = self.last_histogram_type
            else:
                type_to_set = type
            print(type_to_set)
            if type_to_set == HISTOGRAM_TYPES.Continous:
                self._set_histogram_continuous(image)
            if type_to_set == HISTOGRAM_TYPES.Bar:
                self._set_histogram_bar(image)
        except Exception as e:
            print(f"Enconuntered exception while setting histogram {repr(e)}")

    def _set_histogram_bar(self, image):
        color = ('b', 'g', 'r')
        self.figure.clear()

        try:
            b, g, r = cv2.split(image)
            ax1 = self.figure.add_subplot(111)
            ax1.hist([b.ravel(), g.ravel(), r.ravel()], 256,  color=['b', 'g', 'r'])
        except:
            # Grayscale image
            ax1 = self.figure.add_subplot(111)
            ax1.hist(image.ravel(),256, color='black')

        self.canvas.draw()

    def _set_histogram_continuous(self, image):
        color = ('b', 'g', 'r')
        self.figure.clear()
        for i, col in enumerate(color):
            histr = cv2.calcHist([image], [i], None, [256], [0, 256])
            ax = self.figure.add_subplot(111)

            ax.plot(histr, color=col, linewidth=3.0)
            ax.set_ylabel('Y', color='blue')
            ax.set_xlabel('X', color='blue')
            ax.set_title('Histogram')
            ax.grid()
        self.canvas.draw()
