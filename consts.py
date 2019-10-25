import cv2

THRESHOLDINGS = {'Binary':cv2.THRESH_BINARY,
                 'Binary inv':cv2.THRESH_BINARY_INV,
                 'Trunc':cv2.THRESH_TRUNC,
                 'To zero':cv2.THRESH_TOZERO,
                 'To zero inv':cv2.THRESH_TOZERO_INV}