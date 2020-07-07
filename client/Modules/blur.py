import cv2 as cv
import numpy as np
import requests
import io
import matplotlib.pyplot as plt
import base64
import json
import os
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
        URL = os.environ["server_ip"]+"/blur/averaging"
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
        URL = os.environ["server_ip"]+"/blur/gaussian"
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
        URL = os.environ["server_ip"]+"/blur/median"
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
        URL = os.environ["server_ip"]+"/sharpen"
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
