from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.actionbar import ActionDropDown, ActionItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from Modules.grabcut import GrabCut
from Modules.watershed import WaterShed
from Modules.blur import Blur
from Modules.audio import AudioRecorder
from Modules.encodedecodeimg import EncodeDecodeImage

import cv2 as cv
import SimpleITK as sitk
import os
import json
import numpy as np
import requests
from multiprocessing import Process
import sys

STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}
VIDEO_TYPE = {
    'avi': cv.VideoWriter_fourcc(*'XVID'),
    'mp4': cv.VideoWriter_fourcc(*'XVID'),
}

class KivyCamera(BoxLayout):
    cancel = ObjectProperty(None)
    filename = StringProperty('videos/video.avi')
    frames_per_second = NumericProperty(30.0)
    video_resolution = StringProperty('720p')
    flag = True

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.img1=Image()
        self.add_widget(self.img1)
        self.capture = cv.VideoCapture(0)
        self.out = cv.VideoWriter(self.filename, self.get_video_type(self.filename), self.frames_per_second, self.get_dims(self.capture, self.video_resolution))
        if self.flag == True:
            self.event = Clock.schedule_interval(self.update, 1 / self.frames_per_second)
        else:
            cv.destroyAllWindows()
            return
    
    def stop_record(self):
        self.out.release()
        self.capture.release()
        self.flag = False
        self.event.cancel()

    def update(self, *args):
        ret, frame = self.capture.read()
        self.out.write(frame)
        buf = cv.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.img1.texture = texture

    def change_resolution(self, cap, width, height):
        self.capture.set(3, width)
        self.capture.set(4, height)

    def get_dims(self, cap, video_resolution='1080p'):
        width, height = STD_DIMENSIONS["480p"]
        if self.video_resolution in STD_DIMENSIONS:
            width, height = STD_DIMENSIONS[self.video_resolution]
        self.change_resolution(cap, width, height)
        return width, height

    def get_video_type(self, filename):
        filename, ext = os.path.splitext(filename)
        if ext in VIDEO_TYPE:
          return  VIDEO_TYPE[ext]
        return VIDEO_TYPE['avi']

class ActionTextInput(TextInput, ActionItem):
    pass

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class PopupWatershed(FloatLayout):
    cancel = ObjectProperty(None)

class Recorder(FloatLayout):
    start_recording = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    cancel = ObjectProperty(None)
    save = ObjectProperty(None)

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    def __init__(self):
        super(Root, self).__init__()
        self.path = None
        self.updated_image = None
        self.original_image = None
        self.original_path = None
        self.alpha = 1
        self.beta = 0
        self.itr = 0
        self.path_list = list()
        self.audio_object = None

    def dismiss_popup(self):
        self._popup.dismiss()
    
    def quit(self):
        for i in self.path_list:
            os.remove(i)
        App.get_running_app().stop()
    
    def use_watershed(self):
        try:
            img = cv.imread(self.path)
            ws = WaterShed(img)
            path = ws.run()
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.updated_image = cv.imread(path)
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    
    def use_grabcut(self):
        try:
            img = cv.imread(self.path)
            gc = GrabCut(img)
            path = gc.run()
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.updated_image = cv.imread(path)
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    def zoom_image(self, scale):
        self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
        self.rect.size = (scale*400,scale*400)
        print(self.path)
        self.rect.source = self.path
        print(self.rect.source)
        return

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def show_watershed_inst(self):
        content = PopupWatershed()
        self._popup = Popup(title="How to use", content = content,
                            size_hint=(0.9,0.9))
        self._popup.open()
    
    def show_recorder(self):
        content = Recorder(start_recording = self.start_recording, cancel = self.dismiss_popup)
        self._popup = Popup(title="Record Audio", content = content,
                            size_hint=(0.4,0.4))
        self._popup.open()
    def show_vid_recorder(self):
        content = KivyCamera(cancel = self.dismiss_popup)
        self._popup = Popup(title="Record Video", content = content,
                            size_hint=(0.9,0.9))
        self._popup.open()

    def show_save(self):
        # cv.imwrite('output.png',self.updated_image)
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save", content = content,
                            size_hint=(0.9,0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.path = stream.name
            self.original_path = self.path
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = self.path 
            self.updated_image = cv.imread(self.path)    
            self.original_image = self.updated_image  
        self.dismiss_popup()

    def save(self, path, filename):
        # print("yaha tak aaya")
        try:
            with open(os.path.join(path, filename), 'w') as stream:
                # print(stream.name)
                cv.imwrite(stream.name,self.updated_image)
            self.dismiss_popup()
        except Exception as e:
            print(e)
    
    def reset(self):
        try:
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = self.original_path
            self.updated_image = cv.imread(self.original_path)
            self.original_image = self.updated_image
            self.path = self.original_path
        except Exception as e:
            print(e)

    def use_blur_avg(self, kernel):
        try:
            blur = Blur(self.updated_image)
            self.updated_image = blur.averaging(int(kernel))
            del blur
            self.itr += 1
            cv.imwrite('tmp(%d).png'%self.itr,self.updated_image)
            path = os.getcwd() + '/tmp(%d).png'%self.itr
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)

    def use_blur_gaus(self, kernel):
        try:
            blur = Blur(self.updated_image)
            self.updated_image = blur.gaussian(int(kernel))
            del blur
            self.itr += 1
            cv.imwrite('tmp(%d).png'%self.itr,self.updated_image)
            path = os.getcwd() + '/tmp(%d).png'%self.itr
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)

    
    def use_blur_med(self, kernel):
        try:
            blur = Blur(self.updated_image)
            self.updated_image = blur.median(int(kernel))
            del blur
            self.itr += 1
            cv.imwrite('tmp(%d).png'%self.itr,self.updated_image)
            path = os.getcwd() + '/tmp(%d).png'%self.itr
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    
    def use_blur_bil(self):
        try:
            blur = Blur(self.updated_image)
            self.updated_image = blur.bilateral()
            del blur
            cv.imwrite('temp4.png',self.updated_image)
            path = os.getcwd() + '/temp4.png'
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    
    def use_sharpen(self):
        try:
            blur = Blur(self.updated_image)
            self.updated_image = blur.sharpen()
            del blur
            cv.imwrite('temp5.png',self.updated_image)
            path = os.getcwd() + '/temp5.png'
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)

    def use_threshold(self):
        try:
            m = self.updated_image.shape
            obj = EncodeDecodeImage()
            enc_img = obj.encode(self.updated_image)
            data = {
                'img': enc_img,
                'row': m[0],
                'cols': m[1],
                'channels': m[2]
            }
            URL = "http://127.0.0.1:8000/threshold"
            r = requests.post(
                url = URL,
                headers = {"Content-Type": 'application/json',
                            "accept": 'application/json'},
                data=json.dumps(data)  
            )
            print(r.status_code)
            data = r.json()
            self.updated_image = obj.decode(data['img'], m[0], m[1], m[2])
            cv.imwrite('thr.png',self.updated_image)
            path = os.getcwd() + '/thr.png'
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    def use_negative(self):
        try:
            m = self.updated_image.shape
            obj = EncodeDecodeImage()
            enc_img = obj.encode(self.updated_image)
            data = {
                'img': enc_img,
                'row': m[0],
                'cols': m[1],
                'channels': m[2]
            }
            URL = "http://127.0.0.1:8000/negative"
            r = requests.post(
                url = URL,
                headers = {"Content-Type": 'application/json',
                            "accept": 'application/json'},
                data=json.dumps(data)  
            )
            print(r.status_code)
            data = r.json()
            self.updated_image = obj.decode(data['img'], m[0], m[1], m[2])
            cv.imwrite('neg.png',self.updated_image)
            path = os.getcwd() + '/neg.png'
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            self.path_list.append(path)
            return    
        except Exception as e:
            print(e)

    def adjust_image(self,alpha, beta):
        try:
            self.itr += 1
            if alpha != -1:
                self.alpha = alpha
            if beta != -1:
                self.beta = beta
            self.updated_image = cv.convertScaleAbs(self.original_image, alpha=self.alpha, beta=self.beta)
            cv.imwrite('tmp(%d).png'%self.itr,self.updated_image)
            path = os.getcwd() + '/tmp(%d).png'%self.itr
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = path
            self.path = path
            # os.remove(path)
            self.path_list.append(path)
            return
        except Exception as e:
            print(e)
    def start_recording(self, rec_time):
        # print("check")
        self.audio_object =  AudioRecorder(rec_time)
        p1 = Process(target = self.audio_object.record)
        p1.start()
        


    def stop_recording(self):
        # self.audio_object.flag = False
        self.audio_object.stop_record()
        self.audio_object = None
        self.dismiss_popup()
    
    



class InteractiveSegmentationApp(App):
    def build(self):
        return Root()
        


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == '__main__':
    m = InteractiveSegmentationApp()
    m.run()