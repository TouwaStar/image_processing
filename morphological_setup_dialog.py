
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

class MorphologySetupDialog(QDialog):
    def __init__(self,cv_image, parent = None):
        try:
            super().__init__(parent)
            self.original_cv_image = cv_image
            self.working_image = self.original_cv_image
            self.cv_image = self.original_cv_image

            self.main_layout = QGridLayout()
            self.setLayout(self.main_layout)
            self.mask_layout = QGridLayout()
            self.input_fields = []
            # self.main_layout.addLayout(self.mask_layout,0,1)

            self.set_mask_layout(3,3)

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

            erode_button = QPushButton("Apply Erosion")
            dilate_button = QPushButton("Apply Dilation")
            opening_button = QPushButton("Apply Opening")
            closing_button = QPushButton("Apply Closing")
            erode_button.clicked.connect(self._apply_erosion)
            dilate_button.clicked.connect(self._apply_dilation)
            opening_button.clicked.connect(self._apply_opening)
            closing_button.clicked.connect(self._apply_closing)

            special_masks_layout = QHBoxLayout()
            special_masks_layout.addWidget(erode_button)
            special_masks_layout.addWidget(dilate_button)
            special_masks_layout.addWidget(opening_button)
            special_masks_layout.addWidget(closing_button)

            self.main_layout.addWidget(buttonBox,2,1)
            self.main_layout.addLayout(image_setting_layout,2,2)
            self.main_layout.addLayout(special_masks_layout,2,0)

            self.radio_button = QRadioButton("Constant border type")
            self.radio_button2 = QRadioButton("Multiply border type")
            self.radio_button3 = QRadioButton("Reflect border type")
            self.radio_button.setChecked(True)
            box_layout = QHBoxLayout()

            box_layout.addWidget(self.radio_button)
            box_layout.addWidget(self.radio_button2)
            box_layout.addWidget(self.radio_button3)
            self.main_layout.addLayout(box_layout,1,1)

            mask_scale_box = QVBoxLayout()
            self.mask_scale_x = QLineEdit(self)
            self.mask_scale_x.setText('3')
            self.mask_scale_x_label = QLabel("X")
            mask_scale_x_layout = QHBoxLayout()
            mask_scale_x_layout.addWidget(self.mask_scale_x_label)
            mask_scale_x_layout.addWidget(self.mask_scale_x)

            self.mask_scale_y = QLineEdit(self)
            self.mask_scale_y.setText('3')
            self.mask_scale_y_label = QLabel("Y")
            mask_scale_y_layout = QHBoxLayout()
            mask_scale_y_layout.addWidget(self.mask_scale_y_label)
            mask_scale_y_layout.addWidget(self.mask_scale_y)

            # self.mask_scale = QLineEdit(self)
            # self.mask_scale.setText('1')
            # self.mask_scale_label = QLabel("Scale")
            # mask_scale_layout = QHBoxLayout()
            # mask_scale_layout.addWidget(self.mask_scale_label)
            # mask_scale_layout.addWidget(self.mask_scale)

            self.mask_scale_x.textChanged.connect(self.mask_scale_changed)
            self.mask_scale_y.textChanged.connect(self.mask_scale_changed)

            mask_scale_box.addLayout(mask_scale_x_layout)
            mask_scale_box.addLayout(mask_scale_y_layout)
            # mask_scale_box.addLayout(mask_scale_layout)
            self.main_layout.addLayout(mask_scale_box,0,0)


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

    def mask_scale_changed(self):
        try:
            print(f"Scale changed to {int(self.mask_scale_x.text())} {int(self.mask_scale_y.text())}")
        except:
            self.mask_scale_x.setText('1')
            self.mask_scale_y.setText('1')
        self.set_mask_layout(int(self.mask_scale_x.text()), int(self.mask_scale_y.text()))

    def _apply_erosion(self):
        self.cv_image = self.working_image
        try:
            self.cv_image = cv2.erode(self.cv_image, self._get_current_mask(), iterations=1,borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while applying morphological operation for image {repr(e)}")
        self.set_image()

    def _apply_dilation(self):

        self.cv_image = self.working_image
        try:
            self.cv_image = cv2.dilate(self.cv_image, self._get_current_mask(), iterations=1,borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while applying morphological operation for image {repr(e)}")
        self.set_image()

    def _apply_opening(self):
        self.cv_image = self.working_image
        try:
            self.cv_image = cv2.morphologyEx(self.cv_image,cv2.MORPH_OPEN, self._get_current_mask(), iterations=1,borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while applying morphological operation for image {repr(e)}")
        self.set_image()

    def _apply_closing(self):
        self.cv_image = self.working_image
        try:
            self.cv_image = cv2.morphologyEx(self.cv_image,cv2.MORPH_CLOSE, self._get_current_mask(), iterations=1,borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while applying morphological operation for image {repr(e)}")
        self.set_image()


    def set_image(self):
        try:
            height, width, channels = self.cv_image.shape
            channels = channels * width
            self.mq_image = QImage(self.cv_image, width, height, channels, QImage.Format_RGB888)
        except:
            height, width = self.cv_image.shape
            # calculate the total number of bytes in the frame
            totalBytes = self.cv_image.nbytes

            # divide by the number of rows
            bytesPerLine = int(totalBytes / height)
            print("Grayscale image")
            self.mq_image = QImage(self.cv_image, width, height, bytesPerLine, QImage.Format_Grayscale8)

        aspect_ratio = width / height
        self.image_preview.setFixedSize(400 * aspect_ratio, 400)
        self.image_preview.setPixmap(QPixmap.fromImage(self.mq_image))

    def _get_current_mask(self):
        return np.array([int(self.input_fields[x].text()) for x in range(0,int(self.mask_scale_x.text()) * int(self.mask_scale_y.text()))],np.uint8)

    def _get_current_border_type(self):
        border_type = None
        if self.radio_button.isChecked():
            border_type = cv2.BORDER_CONSTANT
        elif self.radio_button2.isChecked():
            border_type = cv2.BORDER_REPLICATE
        elif self.radio_button3.isChecked():
            border_type = cv2.BORDER_REFLECT

        print(f"Border type {border_type}")
        return border_type

    def getInputs(self):
        return self.working_image
