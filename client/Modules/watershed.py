'''
Keys
----
  1-7   - switch marker color
  SPACE - update segmentation
  r     - reset
  a     - toggle autoupdate
  ESC   - exit
'''
# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv
from Modules.common import Sketcher
import os
import requests
import json
from Modules.encodedecodeimg import EncodeDecodeImage

class WaterShed:
    def __init__(self, img):
        self.img = img
        self.vis = img
        if self.img is None:
            raise Exception('Failed to load image file: %s' % fn)

        h, w = self.img.shape[:2]
        self.markers = np.zeros((h, w), np.int32)
        self.markers_vis = self.img.copy()
        self.cur_marker = 1
        self.colors = np.int32( list(np.ndindex(2, 2, 2)) ) * 255

        self.auto_update = True
        self.sketch = Sketcher('img', [self.markers_vis, self.markers], self.get_colors)

    def get_colors(self):
        return list(map(int, self.colors[self.cur_marker])), self.cur_marker

    def watershed(self):
        m = self.markers.copy()
        shape = self.img.shape
        obj = EncodeDecodeImage()
        enc_img = obj.encode(self.img)
        enc_markers = obj.encode(m)
        data = {
            'img': enc_img,
            'markers': enc_markers,
            'row': shape[0],
            'cols': shape[1],
            'channels': shape[2]
        }
        URL = os.environ["server_ip"]+"/watershed"
        r = requests.post(
            url = URL,
            headers = {"Content-Type": 'application/json',
                        "accept": 'application/json'},
            data=json.dumps(data)  
        )
        print(r.status_code)
        data = r.json()
        m = obj.decode2D_int32(data['markers'], shape[0], shape[1])
        overlay = self.colors[np.maximum(m, 0)]
        self.vis = cv.addWeighted(self.img, 0.5, overlay, 0.5, 0.0, dtype=cv.CV_8UC3)
        cv.imshow('watershed', self.vis)

    def run(self):
        while cv.getWindowProperty('img', 0) != -1 or cv.getWindowProperty('watershed', 0) != -1:
            ch = cv.waitKey(50)
            if ch == 27:
                break
            if ch >= ord('1') and ch <= ord('7'):
                self.cur_marker = ch - ord('0')
                print('marker: ', self.cur_marker)
            if ch == ord(' ') or (self.sketch.dirty and self.auto_update):
                self.watershed()
                self.sketch.dirty = False
            if ch in [ord('a'), ord('A')]:
                self.auto_update = not self.auto_update
                print('auto_update if', ['off', 'on'][self.auto_update])
            if ch in [ord('r'), ord('R')]:
                self.markers[:] = 0
                self.markers_vis[:] = self.img
                self.sketch.show()
            if ch == ord('s'):
                cv.destroyAllWindows()
                cv.imwrite('watershed_output.png', self.vis)
                path = os.getcwd() + '/watershed_output.png'
                cv.destroyAllWindows()
                return path

        cv.destroyAllWindows()


# if __name__ == '__main__':
#     print(__doc__)
#     import sys
#     try:
#         fn = sys.argv[1]
#     except:
#         fn = 'lenna.png'
#     App(cv.samples.findFile(fn)).run()