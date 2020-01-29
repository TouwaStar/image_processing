
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
            self._stop_operations = False
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
            merging = QPushButton("Apply Merging")
            region_growing.clicked.connect(self._select_region)
            merging.clicked.connect(self.apply_merge)

            self.thresholding = QLineEdit(self)
            self.thresholding.setText('1')


            operations_layout = QHBoxLayout()
            operations_layout.addWidget(region_growing)
            operations_layout.addWidget(merging)
            operations_layout.addWidget(self.thresholding)

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
        self._stop_operations = True

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
        try:
            self._stop_operations = False
            cv2.namedWindow('input')
            cv2.setMouseCallback('input', self.on_mouse, 0)
            cv2.imshow('input', self.working_image)
            cv2.waitKey()
            cv2.destroyAllWindows()
            self.cv_image = self.region_growing(self.working_image, self.region_to_operate, int(self.thresholding.text()))
            self.set_image()
        except Exception as e:
            print(f"Encountered exception during segmentation algorithm {repr(e)}")
        print("Done!")

    def get8n(self, x, y, shape):
        out = []
        maxx = shape[1] - 1
        maxy = shape[0] - 1

        # top left
        outx = min(max(x - 1, 0), maxx)
        outy = min(max(y - 1, 0), maxy)
        out.append((outx, outy))

        # top center
        outx = x
        outy = min(max(y - 1, 0), maxy)
        out.append((outx, outy))

        # top right
        outx = min(max(x + 1, 0), maxx)
        outy = min(max(y - 1, 0), maxy)
        out.append((outx, outy))

        # left
        outx = min(max(x - 1, 0), maxx)
        outy = y
        out.append((outx, outy))

        # right
        outx = min(max(x + 1, 0), maxx)
        outy = y
        out.append((outx, outy))

        # bottom left
        outx = min(max(x - 1, 0), maxx)
        outy = min(max(y + 1, 0), maxy)
        out.append((outx, outy))

        # bottom center
        outx = x
        outy = min(max(y + 1, 0), maxy)
        out.append((outx, outy))

        # bottom right
        outx = min(max(x + 1, 0), maxx)
        outy = min(max(y + 1, 0), maxy)
        out.append((outx, outy))

        return out

    def region_growing(self, img, seed, threshold=3):
        shape = img.shape

        outimg = np.zeros_like(img)

        # parameters
        mean_reg = float(img[seed[1], seed[0]])
        size = 1
        pix_area = shape[0] * shape[1]

        contour = []
        contour_val = []
        dist = 0

        orient = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # 4 connectivity
        cur_pix = [seed[0], seed[1]]

        iter = 0
        show_progress = 49

        while dist < threshold and size < pix_area:
            for j in range(4):
                temp_pix = [cur_pix[0] + orient[j][0], cur_pix[1] + orient[j][1]]

                is_in_img = shape[1] > temp_pix[0] > 0 and shape[0] > temp_pix[1] > 0
                if is_in_img and (outimg[temp_pix[1], temp_pix[0]] == 0):
                    contour.append(temp_pix)
                    contour_val.append(img[temp_pix[1], temp_pix[0]])
                    outimg[temp_pix[1], temp_pix[0]] = 150

            dist_list = [abs(i - mean_reg) for i in contour_val]
            dist = min(dist_list)
            index = dist_list.index(min(dist_list))
            size += 1
            outimg[cur_pix[1], cur_pix[0]] = 255

            mean_reg = (mean_reg * size + float(contour_val[index])) / (size + 1)

            cur_pix = contour[index]

            del contour[index]
            del contour_val[index]
            iter += 1
            if iter >= show_progress:
                if self._stop_operations:
                    self._stop_operations = False
                    return self.cv_image
                iter = 0
                self.cv_image = outimg
                print("Refreshing segmentation progress")
                self.set_image()

        return outimg

    def apply_merge(self):
        try:

            self.cv_image = self._merge(self.working_image, int(self.thresholding.text()))
            self.set_image()
        except Exception as e:
            print(f"Encountered exception during segmentation algorithm {repr(e)}")
        print("Done!")

    def _merge(self, img, threshold=3, max_regions=4):
        seed = [0,0]
        shape = img.shape

        out_img = np.zeros_like(img)
        xc_img = np.zeros_like(img)
        num_points_in_reg = [0] * max_regions
        mean_of_reg = [0] * max_regions
        intens_sum_of_reg = [0] * max_regions

        num_of_regions = 1
        merge = 0
        for y in range(seed[0]+1, shape[0]-1):
            for x in range(seed[1]+1, shape[1]-1):
                if x==1 and y ==1:
                    xc_img[y,x] = 1
                    out_img[y,x] = num_of_regions
                    num_points_in_reg[num_of_regions-1] = 1
                    intens_sum_of_reg[num_of_regions-1] = int(img[y,x])
                    mean_of_reg[num_of_regions-1] = img[y,x]
                else:
                    dmin = abs(int(img[y,x]) - mean_of_reg[0])
                    min = 1

                    for dy in range(-1,1):
                        for dx in range(-1,2):
                            if (((x + dx) != x) or ((y+dy) != y)) and (((y+dy) != y) or ((x + dx) != (x + 1))):
                                if xc_img[y+dy,x+dx] != 0:
                                    c = abs(int(img[y,x]) - mean_of_reg[xc_img[y+dy,x+dx]-1])
                                    if c < threshold:
                                        merge = 1
                                        if c < dmin:
                                            dmin = c
                                            min = xc_img[y+dy,x+dx]

                    if merge == 1:
                        m = min
                        xc_img[y,x] = m
                        out_img[y,x] = m
                        num_points_in_reg[m-1] +=1
                        intens_sum_of_reg[m-1] += int(img[y,x])
                        mean_of_reg[m-1] = int(intens_sum_of_reg[m-1]/ num_points_in_reg[m-1])
                    if merge == 0:

                        cmin = 255
                        ml = 1
                        for m in range(1,num_of_regions+1):
                            c = abs(int(img[y,x]) - mean_of_reg[m-1])
                            if c<cmin:
                                cmin = c
                                ml = m
                            if c < threshold:
                                merge = 1
                                xc_img[y,x] = ml
                                out_img[y,x] = ml
                                num_points_in_reg[ml-1] += 1
                                intens_sum_of_reg[ml-1] += int(img[y,x])
                                mean_of_reg[ml-1] = int(intens_sum_of_reg[ml-1] / num_points_in_reg[ml-1])
                        if merge == 0 and (num_of_regions < max_regions):
                            num_of_regions += 1
                            xc_img[y,x] = num_of_regions
                            out_img[y,x] = num_of_regions
                            num_points_in_reg[num_of_regions-1] = 1
                            intens_sum_of_reg[num_of_regions-1] = img[y,x]
                            mean_of_reg[num_of_regions-1] = img[y,x]
                        else:
                            merge = 0
                    else:
                        merge = 0


        for y in range(seed[0], shape[0]):
            for x in range(seed[1], shape[1]):
                for i in range(1, max_regions+1):
                    if i==out_img[y,x]:
                        out_img[y,x] = mean_of_reg[i-1]
        return out_img





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
            self.mq_image = QImage(self.cv_image, width, height, bytesPerLine, QImage.Format_Grayscale8)

        aspect_ratio = width / height
        self.image_preview.setFixedSize(400 * aspect_ratio, 400)
        self.image_preview.setPixmap(QPixmap.fromImage(self.mq_image))
        QApplication.processEvents()

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
