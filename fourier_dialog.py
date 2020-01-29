
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
import time

class FourierDialog(QDialog):
    """Dialog window responsible for fourier and amplitude manipulation"""
    def __init__(self,cv_image, parent = None):
        try:
            super().__init__(parent)
            self.original_cv_image = cv_image
            self.working_image = self.original_cv_image
            self.cv_image = self.original_cv_image

            self.main_layout = QGridLayout()
            self.setLayout(self.main_layout)
            # self._stop_operations = False
            # self.main_layout.addLayout(self.mask_layout,0,1)


            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

            apply_button = QPushButton("Apply Mask")
            apply_button.clicked.connect(self._apply_changes)
            reset_button = QPushButton("Reset Image")
            reset_button.clicked.connect(self._reset_image)

            image_setting_layout = QHBoxLayout()
            image_setting_layout.addWidget(apply_button)
            image_setting_layout.addWidget(reset_button)

            fourier_2x_more = QPushButton("Apply Fourier 2*x")
            fourier_2x_more.clicked.connect(self.fft_2x_more)
            fourier_2x_less = QPushButton("Apply Fourier x/2")
            fourier_2x_less.clicked.connect(self.fft_2x_less)
            fourier_value = QPushButton("Apply Fourier value")
            fourier_value.clicked.connect(self.fft_value)
            self.fourier_value_text = QLineEdit()
            self.fourier_value_text.setText('1')
            # merging.clicked.connect(self.apply_merge)
            #
            # self.thresholding = QLineEdit(self)
            # self.thresholding.setText('1')
            #
            #
            operations_layout = QHBoxLayout()
            operations_layout.addWidget(fourier_2x_more)
            operations_layout.addWidget(fourier_2x_less)
            operations_layout.addWidget(fourier_value)
            operations_layout.addWidget(self.fourier_value_text)
            # operations_layout.addWidget(merging)
            # operations_layout.addWidget(self.thresholding)
            #
            self.main_layout.addWidget(buttonBox,2,1)
            self.main_layout.addLayout(image_setting_layout,2,2)
            self.main_layout.addLayout(operations_layout,2,0)
            #
            #
            #
            # self.region_to_operate = 0,0


            # self.mask_scale = QLineEdit(self)
            # self.mask_scale.setText('1')
            # self.mask_scale_label = QLabel("Scale")
            # mask_scale_layout = QHBoxLayout()
            # mask_scale_layout.addWidget(self.mask_scale_label)
            # mask_scale_layout.addWidget(self.mask_scale)

            self.image_preview = QLabel()
            self.image_preview.setFixedSize(400, 400)
            self.image_preview.setStyleSheet("background-color: white; border: 2px inset grey;")
            self.image_preview.setScaledContents(True)
            self.main_layout.addWidget(self.image_preview,0,2)
            self.set_image()


        except Exception as e:
            print(f"Unable to initialize mask setup dialog {repr(e)}")

    def _reset_image(self):
        self.working_image = self.original_cv_image
        self.cv_image = self.working_image
        self.set_image()

    def _apply_changes(self):
        self.working_image = self.cv_image

    def set_mask_layout(self, x, y):
        for i in reversed(range(self.mask_layout.count())):
            self.mask_layout.itemAt(i).widget().setParent(None)
        self.main_layout.removeItem(self.mask_layout)
        self.mask_layout = QGridLayout()

        self.input_fields = []
        for i in range(0, x*y):
            input_field = QLineEdit(self)
            input_field.setText('1')
            self.input_fields.append(input_field)

        total = -1
        for i in range(0, x):
            for j in range(0, y):
                total += 1
                self.mask_layout.addWidget(self.input_fields[total], i, j)
                print(f"i: {i} j: {j} total: {total}")

        self.main_layout.addLayout(self.mask_layout, 0,1)

    def set_image(self):
        try:
            height, width, channels = self.cv_image.shape
            channels = channels * width
            self.mq_image = QImage(self.cv_image.copy(), width, height, channels, QImage.Format_RGB888)
        except:
            height, width = self.cv_image.shape
            # calculate the total number of bytes in the frame
            totalBytes = self.cv_image.nbytes

            # divide by the number of rows
            bytesPerLine = int(totalBytes / height)
            self.mq_image = QImage(self.cv_image.copy(), width, height, bytesPerLine, QImage.Format_Grayscale8)

        aspect_ratio = width / height
        self.image_preview.setFixedSize(400 * aspect_ratio, 400)
        self.image_preview.setPixmap(QPixmap.fromImage(self.mq_image))
        QApplication.processEvents()

    def fft_2x_more(self):
        """2x Intensify the selected values of spectrum, the selected values are received from a selectROI call on the magnitude spectrum"""
        try:
            spectrum, fshift = self._fft_v()
            magnitude_spectrum = np.asarray(spectrum, dtype=np.uint8)
            r = cv2.selectROI('Magnitude spectrum', magnitude_spectrum, showCrosshair=False)
            cv2.destroyWindow('Magnitude spectrum')
            for x in range(r[0],r[2]+r[0]):
                for y in range(r[1],r[3]+r[1]):
                    fshift[x,y] = fshift[x,y] * 2

            fshift = np.fft.ifftshift(fshift)
            ft_image = np.fft.ifft2(fshift)
            img_back = np.abs(ft_image)
            img_back = np.asarray(img_back, dtype=np.uint8)
            self.cv_image = img_back
            self.set_image()
        except Exception as e:
            cv2.destroyWindow('Magnitude spectrum')


    def fft_2x_less(self):
        """2x DeIntensify the selected values of spectrum, the selected values are received from a selectROI call on the magnitude spectrum"""
        try:
            spectrum, fshift = self._fft_v()
            magnitude_spectrum = np.asarray(spectrum, dtype=np.uint8)
            r = cv2.selectROI('Magnitude spectrum', magnitude_spectrum, showCrosshair=False)
            cv2.destroyWindow('Magnitude spectrum')
            for x in range(r[0], r[2] + r[0]):
                for y in range(r[1], r[3] + r[1]):
                    fshift[x, y] = fshift[x, y] / 2

            fshift = np.fft.ifftshift(fshift)
            ft_image = np.fft.ifft2(fshift)
            img_back = np.abs(ft_image)
            img_back = np.asarray(img_back, dtype=np.uint8)
            self.cv_image = img_back
            self.set_image()
        except:

            cv2.destroyWindow('Magnitude spectrum')

    def fft_value(self):
        """Increase or decrease the selected values of spectrum, the selected values are received from a selectROI call on the magnitude spectrum"""
        try:
            spectrum, fshift = self._fft_v()
            magnitude_spectrum = np.asarray(spectrum, dtype=np.uint8)
            r = cv2.selectROI('Magnitude spectrum', magnitude_spectrum, showCrosshair=False)
            cv2.destroyWindow('Magnitude spectrum')
            for x in range(r[0], r[2] + r[0]):
                for y in range(r[1], r[3] + r[1]):
                    fshift[x, y] = fshift[x, y] + int(self.fourier_value_text.text())

            fshift = np.fft.ifftshift(fshift)
            ft_image = np.fft.ifft2(fshift)
            img_back = np.abs(ft_image)
            img_back = np.asarray(img_back, dtype=np.uint8)
            self.cv_image = img_back
            self.set_image()
        except:
            cv2.destroyWindow('Magnitude spectrum')


    def _fft_v(self):
        """Generic method for retrieving magnitude spectrum and fshift of an image using FFT algorithm"""
        try:
            ft_image = np.fft.fft2(self.cv_image)
            fshift = np.fft.fftshift(ft_image)
            magnitude_spectrum = 20*np.log(np.abs(fshift))
            spectrum = magnitude_spectrum
            return spectrum, fshift
        except Exception as e:
            print(f"Exception during fourier transform {repr(e)}")
        else:
            x = self.cv_image
            N = x.shape[0]
            if np.log2(N) % 1 > 0:
                raise ValueError("must be a power of 2")

            N_min = min(N, 2)

            n = np.arange(N_min)
            k = n[:, None]
            M = np.exp(-2j * np.pi * n * k / N_min)
            X = np.dot(M, x.reshape((N_min, -1)))

            while X.shape[0] < N:
                X_even = X[:, :int(X.shape[1] / 2)]
                X_odd = X[:, int(X.shape[1] / 2):]
                terms = np.exp(-1j * np.pi * np.arange(X.shape[0])
                               / X.shape[0])[:, None]
                X = np.vstack([X_even + terms * X_odd,
                               X_even - terms * X_odd])
            self.cv_image = X
            self.set_image()


    def getInputs(self):
        """Returns the current processing of the image to the image window class"""
        return self.cv_image
