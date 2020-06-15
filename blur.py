import cv2 as cv
import numpy as np

class Blur():
    def __init__(self,image):
        # print("0")
        self.image = image
    def averaging(self):
        # print("1")
        avg_img = cv.blur(self.image,(5,5))
        return avg_img
    def gaussian(self):
        # print("2")
        gausBlur = cv.GaussianBlur(self.image, (5,5),0)
        return gausBlur
    def median(self):
        # print("3")
        medBlur = cv.medianBlur(self.image,5)
        return medBlur
    def bilateral(self):
        # print("4")
        bilFilter = cv.bilateralFilter(self.image,9,75,75)
        return bilFilter
    def sharpen(self):
        # print("5")
        kernel_sharpening = np.array([[-1,-1,-1],[-1, 9,-1],[-1,-1,-1]])
        sharpened = cv.filter2D(self.image, -1, kernel_sharpening)
        return sharpened
