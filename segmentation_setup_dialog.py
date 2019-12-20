
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

class SegmentationSetupDialog(QDialog):
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

            region_growing = QPushButton("Apply Region Growing")
            dilate_button = QPushButton("Apply Dilation")
            region_growing.clicked.connect(self._select_region)

            operations_layout = QHBoxLayout()
            operations_layout.addWidget(region_growing)

            self.main_layout.addWidget(buttonBox,2,1)
            self.main_layout.addLayout(image_setting_layout,2,2)
            self.main_layout.addLayout(operations_layout,2,0)



            self.region_to_operate = 0,0


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

    def mask_scale_changed(self):
        try:
            print(f"Scale changed to {int(self.mask_scale_x.text())} {int(self.mask_scale_y.text())}")
        except:
            self.mask_scale_x.setText('1')
            self.mask_scale_y.setText('1')
        self.set_mask_layout(int(self.mask_scale_x.text()), int(self.mask_scale_y.text()))

    def on_mouse(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.region_to_operate = x,y

    def _select_region(self):

        cv2.namedWindow('input')
        cv2.setMouseCallback('input', self.on_mouse, 0)
        cv2.imshow('input', self.working_image)
        cv2.waitKey()
        cv2.destroyAllWindows()
        self.cv_image = self.region_growing(self.working_image, self.region_to_operate)
        self.set_image()

    def region_growing(self, img, seed):
        # Parameters for region growing
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        region_threshold = 0.2
        region_size = 1
        intensity_difference = 0
        neighbor_points_list = []
        neighbor_intensity_list = []

        # Mean of the segmented region
        region_mean = img[seed]

        # Input image parameters
        height, width = img.shape
        image_size = height * width

        # Initialize segmented output image
        segmented_img = np.zeros((height, width, 1), np.uint8)

        # Region growing until intensity difference becomes greater than certain threshold
        while (intensity_difference < region_threshold) & (region_size < image_size):
            # Loop through neighbor pixels
            for i in range(4):
                # Compute the neighbor pixel position
                x_new = seed[0] + neighbors[i][0]
                y_new = seed[1] + neighbors[i][1]

                # Boundary Condition - check if the coordinates are inside the image
                check_inside = (x_new >= 0) & (y_new >= 0) & (x_new < height) & (y_new < width)

                # Add neighbor if inside and not already in segmented_img
                if check_inside:
                    if segmented_img[x_new, y_new] == 0:
                        neighbor_points_list.append([x_new, y_new])
                        neighbor_intensity_list.append(img[x_new, y_new])
                        segmented_img[x_new, y_new] = 255

            # Add pixel with intensity nearest to the mean to the region
            distance = abs(neighbor_intensity_list - region_mean)
            pixel_distance = min(distance)
            index = np.where(distance == pixel_distance)[0][0]
            segmented_img[seed[0], seed[1]] = 255
            region_size += 1

            # New region mean
            region_mean = (region_mean * region_size + neighbor_intensity_list[index]) / (region_size + 1)

            # Update the seed value
            seed = neighbor_points_list[index]
            # Remove the value from the neighborhood lists
            neighbor_intensity_list[index] = neighbor_intensity_list[-1]
            neighbor_points_list[index] = neighbor_points_list[-1]

        return segmented_img


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
