import cv2
from dataclasses import dataclass
# ToDo
# Wszystkie maski kwadratowe od 3 do 11

THRESHOLDINGS = {'Binary':cv2.THRESH_BINARY,
                 'Binary inv':cv2.THRESH_BINARY_INV,
                 'Trunc':cv2.THRESH_TRUNC,
                 'To zero':cv2.THRESH_TOZERO,
                 'To zero inv':cv2.THRESH_TOZERO_INV}
@dataclass
class HISTOGRAM_TYPES:
    Continous = 'Continous'
    Bar = ['Red', 'Green', 'Blue']

HISTOGRAMS = {'Continous':HISTOGRAM_TYPES.Continous,
                   'Bar':HISTOGRAM_TYPES.Bar,}