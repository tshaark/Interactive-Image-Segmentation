from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.actionbar import ActionDropDown, ActionItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import cv2 as cv
from Modules.grabcut import GrabCut
from Modules.watershed import WaterShed
from Modules.blur import Blur
import SimpleITK as sitk
import os
import numpy as np

class ActionTextInput(TextInput, ActionItem):
    pass

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class PopupWatershed(FloatLayout):
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
            img = sitk.GetImageFromArray(self.updated_image)
            otsu_filter = sitk.OtsuThresholdImageFilter()
            otsu_filter.SetInsideValue(0)
            otsu_filter.SetOutsideValue(1)
            seg = otsu_filter.Execute(img)
            self.overlay = sitk.GetArrayFromImage(seg)
            self.updated_image = np.uint8(self.overlay * 255)
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
            self.updated_image = 255 - self.updated_image
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



class InteractiveSegmentationApp(App):
    def build(self):
        return Root()
        


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == '__main__':
    m = InteractiveSegmentationApp()
    m.run()