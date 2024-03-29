from __future__ import print_function

import numpy as np
import cv2 as cv

import sys
import os
import requests
import json
from Modules.encodedecodeimg import EncodeDecodeImage

class GrabCut():
    BLUE = [255,0,0]        # rectangle color
    RED = [0,0,255]         # PR BG
    GREEN = [0,255,0]       # PR FG
    BLACK = [0,0,0]         # sure BG
    WHITE = [255,255,255]   # sure FG

    DRAW_BG = {'color' : BLACK, 'val' : 0}
    DRAW_FG = {'color' : WHITE, 'val' : 1}
    DRAW_PR_BG = {'color' : RED, 'val' : 2}
    DRAW_PR_FG = {'color' : GREEN, 'val' : 3}

    # setting up flags
    rect = (0,0,1,1)
    drawing = False         # flag for drawing curves
    rectangle = False       # flag for drawing rect
    rect_over = False       # flag to check if rect drawn
    rect_or_mask = 100      # flag for selecting rect or mask mode
    value = DRAW_FG         # drawing initialized to FG
    thickness = 3           # brush thickness
    def __init__(self, image):
        self.img = image

    def onmouse(self, event, x, y, flags, param):
        # Draw Rectangle
        if event == cv.EVENT_MBUTTONDOWN:
            self.rectangle = True
            self.ix, self.iy = x,y

        elif event == cv.EVENT_MOUSEMOVE:
            if self.rectangle == True:
                self.img = self.img2.copy()
                cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
                self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
                self.rect_or_mask = 0

        elif event == cv.EVENT_MBUTTONUP:
            self.rectangle = False
            self.rect_over = True
            cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
            self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
            self.rect_or_mask = 0
            print(" Now press the key 'n' a few times until no further change \n")

        # draw touchup curves

        if event == cv.EVENT_LBUTTONDOWN:
            if self.rect_over == False:
                print("first draw rectangle \n")
            else:
                self.drawing = True
                cv.circle(self.img, (x,y), self.thickness, self.value['color'], -1)
                cv.circle(self.mask, (x,y), self.thickness, self.value['val'], -1)

        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing == True:
                cv.circle(self.img, (x, y), self.thickness, self.value['color'], -1)
                cv.circle(self.mask, (x, y), self.thickness, self.value['val'], -1)

        elif event == cv.EVENT_LBUTTONUP:
            if self.drawing == True:
                self.drawing = False
                cv.circle(self.img, (x, y), self.thickness, self.value['color'], -1)
                cv.circle(self.mask, (x, y), self.thickness, self.value['val'], -1)

    def run(self):
        self.img2 = self.img.copy()                               # a copy of original image
        self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
        self.output = np.zeros(self.img.shape, np.uint8)           # output image to be shown

        # input and output windows
        cv.namedWindow('output')
        cv.namedWindow('input')
        cv.setMouseCallback('input', self.onmouse)
        cv.moveWindow('input', self.img.shape[1]+10,90)

        print(" Instructions: \n")
        print(" Draw a rectangle around the object using right mouse button \n")

        while(1):
            
            cv.imshow('output', self.output)
            cv.imshow('input', self.img)
            k = cv.waitKey(1)

            # key bindings
            if k == 27:         # esc to exit
                break
            elif k == ord('0'): # BG drawing
                print(" mark background regions with left mouse button \n")
                self.value = self.DRAW_BG
            elif k == ord('1'): # FG drawing
                print(" mark foreground regions with left mouse button \n")
                self.value = self.DRAW_FG
            elif k == ord('2'): # PR_BG drawing
                self.value = self.DRAW_PR_BG
            elif k == ord('3'): # PR_FG drawing
                self.value = self.DRAW_PR_FG
            elif k == ord('s'): # save image
                bar = np.zeros((self.img.shape[0], 5, 3), np.uint8)
                res = np.hstack((self.img2, bar, self.img, bar, self.output))
                print(" Result saved as image \n")
                cv.imwrite('grabcut_output.png', self.output)
                path = os.getcwd() + '/grabcut_output.png'
                cv.destroyAllWindows()
                return path
            elif k == ord('r'): # reset everything
                print("resetting \n")
                self.rect = (0,0,1,1)
                self.drawing = False
                self.rectangle = False
                self.rect_or_mask = 100
                self.rect_over = False
                self.value = self.DRAW_FG
                self.img = self.img2.copy()
                self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
                self.output = np.zeros(self.img.shape, np.uint8)           # output image to be shown
            elif k == ord('n'): # segment the image
                print(""" For finer touchups, mark foreground and background after pressing keys 0-3
                and again press 'n' \n""")
                try:
                    bgdmodel = np.zeros((1, 65), np.float64)
                    fgdmodel = np.zeros((1, 65), np.float64)
                    if (self.rect_or_mask == 0):         # grabcut with rect
                        m = self.img2.shape
                        obj = EncodeDecodeImage()
                        enc_img = obj.encode(self.img2)
                        enc_mask = obj.encode(self.mask)
                        data = {
                            'img': enc_img,
                            'mask': enc_mask,
                            'rect': self.rect,
                            'mode': "cv.GC_INIT_WITH_RECT",
                            'row': m[0],
                            'cols': m[1],
                            'channels': m[2],
                        }
                        URL = os.environ["server_ip"]+"/grabcut"
                        r = requests.post(
                            url = URL,
                            headers = {"Content-Type": 'application/json',
                                        "accept": 'application/json'},
                            data=json.dumps(data)  
                        )
                        print(r.status_code)
                        data = r.json()
                        self.mask = obj.decode2D(data['mask'], m[0], m[1])
                        self.rect_or_mask = 1
                    
                    elif (self.rect_or_mask == 1):       # grabcut with mask
                        m = self.img2.shape
                        obj = EncodeDecodeImage()
                        enc_img = obj.encode(self.img2)
                        enc_mask = obj.encode(self.mask)
                        data = {
                            'img': enc_img,
                            'mask': enc_mask,
                            'rect': self.rect,
                            'mode': "cv.GC_INIT_WITH_MASK",
                            'row': m[0],
                            'cols': m[1],
                            'channels': m[2]
                        }
                        URL = os.environ["server_ip"]+"/grabcut"
                        r = requests.post(
                            url = URL,
                            headers = {"Content-Type": 'application/json',
                                        "accept": 'application/json'},
                            data=json.dumps(data)  
                        )
                        print(r.status_code)
                        data = r.json()
                        self.mask = obj.decode2D(data['mask'], m[0], m[1])
                except:
                    import traceback
                    traceback.print_exc()

            mask2 = np.where((self.mask==1) + (self.mask==3), 255, 0).astype('uint8')
            self.output = cv.bitwise_and(self.img2, self.img2, mask=mask2)

        print('Done')
    

# if __name__ == '__main__':
#     print(__doc__)
#     App().run()
#     cv.destroyAllWindows()