
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
from mask_setup_dialog import MaskSetupDialog
from morphological_setup_dialog import MorphologySetupDialog
from segmentation_setup_dialog import SegmentationSetupDialog


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

    def reset_image(self):
        self.cv_image = self._original_image
        self._set_image()

    def set_image_from_file(self):
        try:
            fname = QFileDialog.getOpenFileName(self.main_window, 'Open file',
                                                'c:\\', "Image files (*.jpg *.gif *.tif *.png)")[0]

            print(f"Opening {fname}")
            self.cv_image = cv2.imread(fname)
            cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB, self.cv_image)

            self._original_image = self.cv_image
            self._set_image()
        except Exception as e:
            log.error(repr(e))

    def save_image_to_file(self):
        try:
            fname = QFileDialog.getSaveFileName(self.main_window, 'Save file',
                                                'c:\\', "Image files (*.jpg *.png)")[0]
            print(f"Saving image to {fname}")
            cv2.imwrite(fname,self.cv_image)

        except Exception as e:
            log.error(repr(e))

    def _set_image(self):
        try:
            # print(self.cv_image)
            try:
                height, width, channels = self.cv_image.shape
                channels = channels * width
                print("Colour image")
                self.mq_image = QImage(self.cv_image, width, height, channels, QImage.Format_RGB888)
            except:
                height, width = self.cv_image.shape
                # calculate the total number of bytes in the frame
                totalBytes = self.cv_image.nbytes

                # divide by the number of rows
                bytesPerLine = int(totalBytes / height)
                print("Grayscale image")
                self.mq_image = QImage(self.cv_image, width, height, bytesPerLine, QImage.Format_Grayscale8)

            aspect_ratio = width/height
            self.image.setFixedSize(400 * aspect_ratio, 400)
            self.image.setPixmap(QPixmap.fromImage(self.mq_image))

            self.set_histogram(None)
        except Exception as e:
            print(repr(e))

    def negate_image(self):
        self.cv_image = cv2.bitwise_not(self.cv_image)
        self._set_image()

    def threshold_image(self, type):
        print(f"Performing Thresholding of type {type}")
        try:
            num, ok = QInputDialog.getInt(self.main_window, "Thresholding dialog", "enter thresholding start")
            num2, ok = QInputDialog.getInt(self.main_window, "Thresholding dialog", "enter thresholding end")

            gray = cv2.cvtColor(self.cv_image, cv2.COLOR_RGB2GRAY)
            self.cv_image = gray
            if ok:
                ret, self.cv_image = cv2.threshold(gray, num, num2, type)
                self._set_image()
        except Exception as e:
            print(f"Thresholding failed with error {repr(e)}")

    def set_histogram(self, type):
        print(type)
        self.main_window.histogram_window.set_histogram(self.cv_image, type)

    def change_to_grayscale(self):
        gray = cv2.cvtColor(self.cv_image, cv2.COLOR_RGB2GRAY)
        self.cv_image = gray
        self._set_image()

    def equalize_histogram(self):
        try:
            cv2.equalizeHist(self.cv_image, self.cv_image)
            self._set_image()
        except Exception as e:
            print(f"Equalizing histogram failed with error {repr(e)} image probably not in grayscale retrying")
            self.change_to_grayscale()
            cv2.equalizeHist(self.cv_image, self.cv_image)
            self._set_image()

    def stretch_histogram(self):
        try:
            minmax_img = np.zeros((self.cv_image.shape[0], self.cv_image.shape[1]), dtype='uint8')

            # Loop over the image and apply Min-Max formulae

            min = np.min(self.cv_image)
            max = np.max(self.cv_image)

            for i in range(self.cv_image.shape[0]):
                for j in range(self.cv_image.shape[1]):
                    minmax_img[i, j] = 255 * (self.cv_image[i, j] - min) / (max - min)
            self.cv_image = minmax_img

            self._set_image()

        except Exception as e:
            print(f"Exception while stretching histogram {repr(e)}")

            self.change_to_grayscale()
            self.stretch_histogram()

    def linear_filtering(self):
        try:
            dialog = MaskSetupDialog(self.cv_image)

            if dialog.exec():
                self.cv_image = dialog.getInputs()
                self._set_image()
        except Exception as e:
            print(f"Exception using mask seutp dialog {repr(e)}")

    def morphological_operations(self):
        dialog = MorphologySetupDialog(self.cv_image)

        if dialog.exec():
            self.cv_image = dialog.getInputs()
            self._set_image()

    def segmentation_operations(self):
        dialog = SegmentationSetupDialog(self.cv_image)

        if dialog.exec():
            self.cv_image = dialog.getInputs()
            self._set_image()

    def skeletize(self):
        img = self.cv_image

        skeleton = np.zeros(img.shape, np.uint8)
        eroded = np.zeros(img.shape, np.uint8)
        temp = np.zeros(img.shape, np.uint8)

        _, thresh = cv2.threshold(img, 127, 255, 0)

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        iters = 0
        while (True):
            cv2.erode(thresh, kernel, eroded,borderType=cv2.BORDER_REPLICATE)
            cv2.dilate(eroded, kernel, temp,borderType=cv2.BORDER_REPLICATE)
            cv2.subtract(thresh, temp, temp)
            cv2.bitwise_or(skeleton, temp, skeleton)
            thresh, eroded = eroded, thresh  # Swap instead of copy

            iters += 1
            if cv2.countNonZero(thresh) == 0:
                self.cv_image = skeleton
                self._set_image()
                return


