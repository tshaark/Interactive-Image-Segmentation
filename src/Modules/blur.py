import cv2 as cv
import numpy as np
import requests
import io
import matplotlib.pyplot as plt
import base64
import json
from pydantic import BaseModel
from Modules.encodedecodeimg import EncodeDecodeImage


class Blur():
    def __init__(self,image):
        self.image = image
    
    def averaging(self,k):
        m = self.image.shape
        obj = EncodeDecodeImage()
        enc_img = obj.encode(self.image)
        data = {
            'kernel': k,
            'img': enc_img,
            'row': m[0],
            'cols': m[1],
            'channels': m[2]
        }
        URL = "http://127.0.0.1:8000/blur/averaging"
        r = requests.post(
            url = URL,
            headers = {"Content-Type": 'application/json',
                        "accept": 'application/json'},
            data=json.dumps(data)  
        )
        print(r.status_code)
        data = r.json()
        img = obj.decode(data['img'], m[0], m[1], m[2])
        return img
    
    def gaussian(self, k):
        m = self.image.shape
        obj = EncodeDecodeImage()
        enc_img = obj.encode(self.image)
        data = {
            'kernel': k,
            'img': enc_img,
            'row': m[0],
            'cols': m[1],
            'channels': m[2]
        }
        URL = "http://127.0.0.1:8000/blur/gaussian"
        r = requests.post(
            url = URL,
            headers = {"Content-Type": 'application/json',
                        "accept": 'application/json'},
            data=json.dumps(data)  
        )
        print(r.status_code)
        data = r.json()
        img = obj.decode(data['img'], m[0], m[1], m[2])
        return img
    
    def median(self, k):
        m = self.image.shape
        obj = EncodeDecodeImage()
        enc_img = obj.encode(self.image)
        data = {
            'kernel': k,
            'img': enc_img,
            'row': m[0],
            'cols': m[1],
            'channels': m[2]
        }
        URL = "http://127.0.0.1:8000/blur/median"
        r = requests.post(
            url = URL,
            headers = {"Content-Type": 'application/json',
                        "accept": 'application/json'},
            data=json.dumps(data)  
        )
        print(r.status_code)
        data = r.json()
        img = obj.decode(data['img'], m[0], m[1], m[2])
        return img
    
    def sharpen(self):
        m = self.image.shape
        obj = EncodeDecodeImage()
        enc_img = obj.encode(self.image)
        data = {
            'img': enc_img,
            'row': m[0],
            'cols': m[1],
            'channels': m[2]
        }
        URL = "http://127.0.0.1:8000/sharpen"
        r = requests.post(
            url = URL,
            headers = {"Content-Type": 'application/json',
                        "accept": 'application/json'},
            data=json.dumps(data)  
        )
        print(r.status_code)
        data = r.json()
        img = obj.decode(data['img'], m[0], m[1], m[2])
        return img
