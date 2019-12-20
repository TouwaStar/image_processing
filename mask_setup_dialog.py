
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

class MaskSetupDialog(QDialog):
    def __init__(self,cv_image, parent = None):
        try:
            print("Initializing mask setup dialog")
            super().__init__(parent)
            self.original_cv_image = cv_image
            self.working_image = cv_image
            self.cv_image = cv_image

            self.main_layout = QGridLayout()
            self.setLayout(self.main_layout)
            self.mask_layout = QGridLayout()
            self.input_fields = []
            self.main_layout.addLayout(self.mask_layout,0,1)

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

            sobel_button = QPushButton("Apply Sobel")
            roberts_button = QPushButton("Apply Roberts")
            prewitt_button = QPushButton("Apply Prewitt")
            sobel_button.clicked.connect(self._apply_sobel)
            roberts_button.clicked.connect(self._apply_roberts)
            prewitt_button.clicked.connect(self._apply_prewitt)

            special_masks_layout = QHBoxLayout()
            special_masks_layout.addWidget(sobel_button)
            special_masks_layout.addWidget(roberts_button)
            special_masks_layout.addWidget(prewitt_button)

            self.scale_regular_button = QPushButton("Apply Regular Scaling")
            self.scale_trivalue_button = QPushButton("Apply Trivalue Scaling")
            self.scale_cut_button = QPushButton("Apply Cut Scaling")
            self.scale_regular_button.clicked.connect(self.set_scaling_1)
            self.scale_trivalue_button.clicked.connect(self.set_scaling_2)
            self.scale_cut_button.clicked.connect(self.set_scaling_3)


            self.scaling_scale_min = QLineEdit(self)
            self.scaling_scale_min.setText('0')
            self.scaling_scale_min_label = QLabel("Scaling scale Min")
            scaling_scale_min_layout = QHBoxLayout()
            scaling_scale_min_layout.addWidget(self.scaling_scale_min_label)
            scaling_scale_min_layout.addWidget(self.scaling_scale_min)

            self.scaling_scale_max = QLineEdit(self)
            self.scaling_scale_max.setText('255')
            self.scaling_scale_max_label = QLabel("Scaling scale Max")
            scaling_scale_max_layout = QHBoxLayout()
            scaling_scale_max_layout.addWidget(self.scaling_scale_max_label)
            scaling_scale_max_layout.addWidget(self.scaling_scale_max)

            self.scaling_set_image_vals = QPushButton("Apply Image Min/Max")
            self.scaling_set_image_vals.clicked.connect(self.set_scaling_min_max_image)


            scaling_scale_layout = QHBoxLayout()
            scaling_scale_layout.addLayout(scaling_scale_min_layout)
            scaling_scale_layout.addLayout(scaling_scale_max_layout)
            scaling_scale_layout.addWidget(self.scaling_set_image_vals)


            scaling_masks_layout = QHBoxLayout()
            scaling_masks_layout.addWidget(self.scale_regular_button)
            scaling_masks_layout.addWidget(self.scale_trivalue_button)
            scaling_masks_layout.addWidget(self.scale_cut_button)

            self.main_layout.addWidget(buttonBox,2,1)
            self.main_layout.addLayout(image_setting_layout,3,3)
            self.main_layout.addLayout(special_masks_layout,3,0)
            self.main_layout.addLayout(scaling_masks_layout,2,0)
            self.main_layout.addLayout(scaling_scale_layout,1,0)

            self.radio_button = QRadioButton("Constant border type")
            self.radio_button2 = QRadioButton("Multiply border type")
            self.radio_button3 = QRadioButton("Reflect border type")
            self.radio_button.setChecked(True)
            self.radio_button.toggled.connect(self.set_filter)
            self.radio_button2.toggled.connect(self.set_filter)
            self.radio_button3.toggled.connect(self.set_filter)
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

            self.mask_scale = QLineEdit(self)
            self.mask_scale.setText('1')
            self.mask_scale_label = QLabel("Scale")
            mask_scale_layout = QHBoxLayout()
            mask_scale_layout.addWidget(self.mask_scale_label)
            mask_scale_layout.addWidget(self.mask_scale)

            self.mask_scale_x.textChanged.connect(self.mask_scale_changed)
            self.mask_scale_y.textChanged.connect(self.mask_scale_changed)

            mask_scale_box.addLayout(mask_scale_x_layout)
            mask_scale_box.addLayout(mask_scale_y_layout)
            mask_scale_box.addLayout(mask_scale_layout)
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
        print("Reseting image")
        print(self.original_cv_image)
        self.working_image = self.original_cv_image
        self.cv_image = self.working_image
        self.set_image()

    def set_scaling_min_max_image(self):
        self.scaling_scale_max.setText(str(np.max(self.working_image)))
        self.scaling_scale_min.setText(str(np.min(self.working_image)))

    def set_scaling_1(self):
        self.set_scaling(1)
    def set_scaling_2(self):
        self.set_scaling(2)
    def set_scaling_3(self):
        self.set_scaling(3)

    def set_scaling(self, scale):
        img_to_scale = self.working_image.copy()

        min = np.min(img_to_scale)
        max = np.max(img_to_scale)

        scaling_method = scale

        print(f"EX {img_to_scale[0,0]}")
        print(f"Setting scaling method {scaling_method}")
        print(f"Prev {img_to_scale}")
        try:
            for i in range(img_to_scale.shape[0]):
                for j in range(img_to_scale.shape[1]):
                    img_to_scale[i, j] = self._calculate_scaling(img_to_scale[i,j],min,max,scaling_method)
        except Exception as e:
            print("Can't handle color images")
            return

        print(f"Next {img_to_scale}")
        self.cv_image = img_to_scale
        self.set_image()

    def _calculate_scaling(self, oldLevel, min, max, method):
        SCALE_MIN = int(self.scaling_scale_min.text())
        SCALE_MAX = int(self.scaling_scale_max.text())
        NO_SCALING = 0
        REGULAR = 1
        TRIVALUE = 2
        CUT = 3

        if method == REGULAR:
            return ((oldLevel - min) / (max - min)) * SCALE_MAX
        elif method == TRIVALUE:
            if oldLevel < SCALE_MIN:
                return SCALE_MIN
            if oldLevel == SCALE_MIN:
                return SCALE_MAX / 2
            return SCALE_MAX
        elif method == CUT:
            if oldLevel < SCALE_MIN:
                return SCALE_MIN
            if oldLevel <= SCALE_MAX:
                return oldLevel
            return SCALE_MAX
        return oldLevel

    def _apply_roberts(self):
        self.cv_image = self.working_image
        try:
            mask = [1,0,0,-1]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image1 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        try:
            mask = [0,-1,1,0]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image2 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        self.cv_image = cv2.addWeighted(cv_image1,0.5,cv_image2,0.5, 2)
        self._apply_changes()
        self.set_image()

    def _apply_sobel(self):
        self.cv_image = self.working_image
        try:
            mask = [-1,0,1,-2,0,2,-1,0,1]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image1 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        try:
            mask = [-1,-2,-1,0,0,0,1,2,1]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image2 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        self.cv_image = cv2.addWeighted(cv_image1,0.5,cv_image2,0.5, 2)
        self._apply_changes()
        self.set_image()

    def _apply_prewitt(self):
        self.cv_image = self.working_image
        try:
            mask = [1,0,-1,1,0,-1,1,0,-1]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image1 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        try:
            mask = [1,1,1,0,0,0,-1,-1,-1]
            kernel = np.array(mask, dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            cv_image2 = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
            return
        self.cv_image = cv2.addWeighted(cv_image1,0.5,cv_image2,0.5, 2)
        self._apply_changes()
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
            input_field.textChanged.connect(self.set_filter)
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
        self.set_filter()

    def set_filter(self):
        self.cv_image = self.working_image
        try:
            kernel = np.array(self._get_current_mask(), dtype=np.float32)
            if kernel.sum() != 0:
                kernel /= kernel.sum()
            self.cv_image = cv2.filter2D(self.cv_image, -1, kernel, borderType=self._get_current_border_type())
        except Exception as e:
            print(f"Exception while creating linear filter for image {repr(e)}")
        self.set_image()

    def set_image(self):
        print(f"Setting image {self.cv_image}")
        try:
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
        except Exception as e:
            print(f"Failed setting image {repr(e)}")

    def _get_current_mask(self):
        return [self.input_fields[x].text() for x in range(0,int(self.mask_scale_x.text()) * int(self.mask_scale_y.text()))]

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
