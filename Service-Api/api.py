from __future__ import print_function
from fastapi import FastAPI, File, UploadFile, Body, Depends
from fastapi import Path
import uvicorn
from starlette.responses import StreamingResponse
from pydantic import BaseModel
import cv2 as cv
import numpy as np
import io
import os
from pydantic import BaseModel
import base64
import SimpleITK as sitk
from fastapi.middleware.cors import CORSMiddleware
from encodedecodeimg import EncodeDecodeImage
app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Data(BaseModel):
    kernel: int = None
    img: str
    row: int
    cols: int
    channels: int



@app.post('/blur/test')
def blur(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = cv.blur(img, (data.kernel, data.kernel))
    img = obj.encode(img)
    return {'img': img}


@app.post('/blur/averaging')
def avg_blur(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = cv.blur(img, (data.kernel, data.kernel))
    img = obj.encode(img)
    return {'img': img}
    

@app.post('/blur/gaussian')
def gaus_blur(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = cv.GaussianBlur(img, (data.kernel,data.kernel),0)
    img = obj.encode(img)
    return {'img': img}
    

@app.post('/blur/median')
def med_blur(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = cv.medianBlur(img, data.kernel)
    img = obj.encode(img)
    return {'img': img}
    

@app.post('/sharpen')
def sharpen(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    kernel_sharpening = np.array([[-1,-1,-1],[-1, 9,-1],[-1,-1,-1]])
    img = cv.filter2D(img, -1, kernel_sharpening)
    img = obj.encode(img)
    return {'img': img}

@app.post('/threshold')
def threshold(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = sitk.GetImageFromArray(img)
    otsu_filter = sitk.OtsuThresholdImageFilter()
    otsu_filter.SetInsideValue(0)
    otsu_filter.SetOutsideValue(1)
    seg = otsu_filter.Execute(img)
    overlay = sitk.GetArrayFromImage(seg)
    image = np.uint8(overlay * 255)
    image = obj.encode(image)
    return {'img': image}

@app.post('/negative')
def negative(data: Data):
    obj = EncodeDecodeImage()
    img = obj.decode(data.img, data.row, data.cols, data.channels)
    img = 255 - img
    img = obj.encode(img)
    return {'img': img}


################################################################################################
class DataGrabCut(BaseModel):
    img: str
    mask: str
    rect: tuple
    mode: str
    row: int
    cols: int
    channels: int


@app.post('/grabcut')
def grabcut(datagrabcut: DataGrabCut):
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    obj = EncodeDecodeImage()
    img = obj.decode(datagrabcut.img, datagrabcut.row, datagrabcut.cols, datagrabcut.channels)
    mask = obj.decode2D(datagrabcut.mask, datagrabcut.row, datagrabcut.cols)
    if datagrabcut.mode == "cv.GC_INIT_WITH_RECT":
        cv.grabCut(img, mask, datagrabcut.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_RECT)
    else:
        cv.grabCut(img, mask, datagrabcut.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_MASK)
    mask = obj.encode(mask)
    return {'mask': mask}


################################################################################################
class DataWatershed(BaseModel):
    img: str
    markers: str = None
    row: int
    cols: int
    channels: int

@app.post('/watershed')
def watershed(datawatershed: DataWatershed):
    obj = EncodeDecodeImage()
    img = obj.decode(datawatershed.img, datawatershed.row, datawatershed.cols, datawatershed.channels)
    markers = obj.decode2D_int32(datawatershed.markers, datawatershed.row, datawatershed.cols)
    cv.watershed(img, markers)
    markers = obj.encode(markers)
    return {'markers': markers}

