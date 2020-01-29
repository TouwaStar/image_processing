
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
import math

class ShapeDescriptorsDialog(QDialog):
    def __init__(self,cv_image, parent = None):
        try:
            print("Initializing mask setup dialog")
            super().__init__(parent)
            self.original_cv_image = cv_image
            self.working_image = cv_image
            self.cv_image = cv_image

            self.main_layout = QGridLayout()
            self.setLayout(self.main_layout)

            moments = cv2.moments(self.cv_image, True)

            self.normal_moments = QTextEdit()
            self.normal_moments.setText(f"Normal Moments:"
                                        f" \nm00={moments['m00']}  \nm10={moments['m10']} \nm01={moments['m01']}"
                                        f" \nm20={moments['m20']} \nm11={moments['m11']} \nm02={moments['m02']}"
                                        f" \nm30={moments['m30']} \nm21={moments['m21']} \nm12={moments['m12']}"
                                        f" \nm03={moments['m03']}")
            self.main_layout.addWidget(self.normal_moments)


            self.central_moments = QTextEdit()
            self.central_moments.setText(f"Central Moments:"
                                        f" \nM20={moments['mu20']}  \nM11={moments['mu11']} \nM02={moments['mu02']}"
                                        f" \nM30={moments['mu30']} \nM21={moments['mu21']} \nM12={moments['mu12']}"
                                        f" \nM03={moments['mu03']}")
            self.main_layout.addWidget(self.central_moments)


            self.normalized_moments = QTextEdit()
            self.normalized_moments.setText(f"Normalized Moments:"
                                         f" \nN20={moments['nu20']}  \nN11={moments['nu11']} \nN02={moments['nu02']}"
                                         f" \nN30={moments['nu30']} \nN21={moments['mu21']} \nN12={moments['nu12']}"
                                         f" \nN03={moments['nu03']}")
            self.main_layout.addWidget(self.normalized_moments)

            self.hu_moments = QTextEdit()
            hu = cv2.HuMoments(moments)

            self.hu_moments.setText(f"Hu Moments:"
                                         f" \nM1={hu[0][0]}  \nM2={hu[1][0]} \nM3={hu[2][0]}"
                                         f" \nM4={hu[3][0]} \nM5={hu[4][0]} \nM6={hu[5][0]}"
                                         f" \nM7={hu[6][0]}")
            self.main_layout.addWidget(self.hu_moments)

            self.shape_features = QTextEdit()
            self.shape_features.setText(self.calculate_shape_features(moments))
            self.main_layout.addWidget(self.shape_features)

            # Shape features


        except Exception as e:
            print(f"Unable to initialize mask setup dialog {repr(e)}")

    def get_distance(self, point_a, point_b):
        x_diff = point_a[0] - point_b[0]
        y_diff = point_a[1] - point_b[1]
        return math.sqrt(x_diff * x_diff + y_diff * y_diff)

    def calculate_shape_features(self, moments):
        cx = moments['m10'] / moments['m00']
        cy = moments['m01'] / moments['m00']
        countours, hierarchy = cv2.findContours(self.cv_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        object_contour = countours[1]
        contour_area = cv2.contourArea(object_contour)
        arc_len = cv2.arcLength(object_contour, True)
        contour_to_center_distance_min = 1
        contour_to_center_distance_max = 0
        sum_of_contour_to_center_distances = 0
        sum_of_contour_to_center_distance_powers = 0
        sum_of_point_to_center_distances = 0
        min_point_to_contour_distance_sum = 0
        max_dimension = 0
        contour_point_count = len(object_contour)

        for col in range(0, self.cv_image.shape[1]):
            for row in range(0, self.cv_image.shape[0]):
                result = cv2.pointPolygonTest(object_contour, (row, col), False)
                if result > 0:
                    dist = self.get_distance([cx, cy], [row, col])
                    sum_of_point_to_center_distances += dist

                    min_distance_to_contour = 1
                    for point in object_contour:
                        contour_distance = self.get_distance([row, col], point[0])
                        if contour_distance < min_distance_to_contour:
                            min_distance_to_contour = contour_distance
                    min_point_to_contour_distance_sum += min_distance_to_contour

        for point in object_contour:
            dist = self.get_distance([cx, cy], point[0])

            if dist > contour_to_center_distance_max:
                contour_to_center_distance_max = dist
            if dist < contour_to_center_distance_min:
                contour_to_center_distance_min = dist

            sum_of_contour_to_center_distances += dist
            sum_of_contour_to_center_distance_powers += dist * dist

            for point2 in object_contour:
                dist_p2 = self.get_distance(point[0], point2[0])
                if dist_p2 > max_dimension:
                    max_dimension = dist_p2

        w1 = 2 * math.sqrt(contour_area / math.pi)
        w2 = arc_len / math.pi
        w3 = (arc_len / (2 * math.sqrt(math.pi * contour_area))) -1
        w4 = contour_area / (math.sqrt(2 * math.pi * sum_of_point_to_center_distances))
        w5 = (contour_area * contour_area * contour_area) / (min_point_to_contour_distance_sum * min_point_to_contour_distance_sum)
        w6 = math.sqrt((sum_of_contour_to_center_distances * sum_of_contour_to_center_distances)
                  / (contour_point_count * sum_of_contour_to_center_distance_powers - 1))
        w7 = contour_to_center_distance_min / contour_to_center_distance_max
        w8 = max_dimension / arc_len
        w9 = (2 * math.sqrt(math.pi * contour_area)) / arc_len

        return f"Shape Features:" \
               f"\nW1={w1}" \
               f"\nW2={w2}"\
               f"\nW3={w3}"\
               f"\nW4={w4}"\
               f"\nW5={w5}"\
               f"\nW6={w6}"\
               f"\nW7={w7}"\
               f"\nW8={w8}"\
               f"\nW9={w9}"


    def _reset_image(self):
        """Resets the image to the one first passed when initializing the class """
        print("Reseting image")
        print(self.original_cv_image)
        self.working_image = self.original_cv_image
        self.cv_image = self.working_image
        self.set_image()


    def set_image(self):
        """Same as the method in image_window, it sets the result of operations on cv_image as displayed image"""
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
        """Returns the values currently set in the mask input fields"""
        return [self.input_fields[x].text() for x in range(0,int(self.mask_scale_x.text()) * int(self.mask_scale_y.text()))]

    def _get_current_border_type(self):
        """Returns currently set border type from radio buttons"""
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
        """Class return value, used when the window closes and operations return to image_window"""
        return self.working_image
