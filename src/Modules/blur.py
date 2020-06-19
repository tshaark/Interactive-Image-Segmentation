import cv2 as cv
import numpy as np

class Blur():
    def __init__(self,image):
        # print("0")
        self.image = image
    def averaging(self,k):
        # print("1")
        avg_img = cv.blur(self.image,(k,k))
        return avg_img
    def gaussian(self, k):
        # print("2")
        gausBlur = cv.GaussianBlur(self.image, (k,k),0)
        return gausBlur
    def median(self, k):
        # print("3")
        medBlur = cv.medianBlur(self.image,k)
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
