import numpy as np
import base64

class EncodeDecodeImage():
    def __init__(self):
        pass
    
    def encode(self, img):
        img = np.float64(img)
        enc_img = img.tostring()
        enc_img = base64.b64encode(enc_img).decode('UTF-8')
        return enc_img
    
    def decode(self, img, m, n, o):
        img = img.encode('UTF-8')
        img = base64.b64decode(img)
        img = np.fromstring(img)
        img = np.uint8(img)
        img = np.reshape(img, (m,n,o))
        return img
    
    def decode2D(self, img, m, n):
        img = img.encode('UTF-8')
        img = base64.b64decode(img)
        img = np.fromstring(img)
        img = np.uint8(img)
        img = np.reshape(img, (m,n))
        return img
    def decode2D_int32(self, img, m, n):
        img = img.encode('UTF-8')
        img = base64.b64decode(img)
        img = np.fromstring(img)
        img = np.int32(img)
        img = np.reshape(img, (m,n))
        return img
