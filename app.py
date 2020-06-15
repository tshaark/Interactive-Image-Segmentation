from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.actionbar import ActionDropDown
from kivy.uix.label import Label
from kivy.uix.button import Button
import cv2 as cv
from grabcut import GrabCut
from watershed import WaterShed

import os



class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class PopupWatershed(FloatLayout):
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    def __init__(self):
        super(Root, self).__init__()
        self.cvimage = None
        self.update_image = None

    def dismiss_popup(self):
        self._popup.dismiss()
    def quit(self):
        App.get_running_app().stop()
    def use_watershed(self):
        # self.show_watershed_inst()
        img = cv.imread(self.cvimage)
        ws = WaterShed(img)
        path = ws.run()
        self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
        self.rect.source = path
        self.update_image = cv.imread(path)
        return
    
    def use_grabcut(self):
        img = cv.imread(self.cvimage)
        gc = GrabCut(img)
        path = gc.run()
        self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
        self.rect.source = path
        self.update_image = cv.imread(path)
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
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.cvimage = stream.name
            self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
            self.rect.source = stream.name 
                
                
        self.dismiss_popup()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()
    
    def reset(self):
        self.rect = self.ids.w_canvas.canvas.get_group('b')[0]
        self.rect.source = self.cvimage
        


class MyApp(App):
    def build(self):
        return Root()
        


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == '__main__':
    m = MyApp()
    m.run()