#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import mkdir, listdir
from os.path import exists, abspath, dirname, join, isfile, splitext
from json import load
from lackey import SettingsMaster, App, FindFailed
from cv2 import imread, resize, imwrite  # pylint: disable=e0611

SettingsMaster.InfoLogs = False
SettingsMaster.ActionLogs = False


class AppEx(App):
    @staticmethod
    def resize_images(src_dir, des_dir, factor):
        for item in listdir(src_dir):
            src_path = join(src_dir, item)
            if isfile(src_path):
                ext = splitext(src_path)[1]
                if ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                    des_path = join(des_dir, item)
                    src_image = imread(src_path)
                    des_image = resize(src_image, None, fx=factor, fy=factor)
                    imwrite(des_path, des_image)

    def run_json(self, path, times=1, index=0):
        img_dir = dirname(abspath(path))
        with open(path) as file:
            json = load(file)
            events = json.get('events')
            start = json.get('start')
            window = self.window(index)
            if events and start and window:
                w = window.getW()
                h = window.getH()
                print(w, h)
                width = json.get('width')
                height = json.get('height')
                if width and height:
                    tmp_dir = '{0}_{1}x{2}_tmp'.format(img_dir, w, h)
                    if not exists(tmp_dir):
                        mkdir(tmp_dir)
                        fx = w / width
                        fy = h / height
                        factor = (fx + fy) / 2
                        self.resize_images(img_dir, tmp_dir, factor)
                    img_dir = tmp_dir
                for i in range(times):
                    handler = EventHandler(window, events, img_dir, start)
                    handler.run_all()


class EventHandler():
    def __init__(self, region, events, img_dir, name):
        self.region = region
        self.events = events
        self.img_dir = img_dir
        self.name = name

    def try_find(self, pattern, wait=0):
        try:
            self.region.setAutoWaitTimeout(wait)
            return self.region.findBest(pattern)
        except FindFailed:
            pass

    def run_once(self):
        event = self.events.get(self.name)
        if event:
            loop = event.get('__loop__', 1)
            sleep = event.get('__sleep__', 0)
            wait = event.get('__wait__', 3)
            delay = event.get('__delay__', 0)
            max_name = None
            for i in range(loop):
                max_score = 0
                max_match = None
                self.region.wait(sleep)
                for key, value in event.items():
                    if key.startswith('__') and key.endswith('__'):
                        continue
                    img_path = join(self.img_dir, key)
                    match = self.try_find(img_path, wait)
                    if match:
                        score = match.getScore()
                        if score > max_score:
                            max_score = score
                            max_match = match
                            max_name = value
                if max_match:
                    self.region.wait(delay)
                    max_match.click()
                    print(self.name, ':', key, '->', value)
                else:
                    break
            if max_name:
                self.name = max_name
            else:
                self.name = event.get('__none__', '__end__')
        else:
            self.name = '__end__'

    def run_all(self):
        for i in range(1024):
            if self.name != '__end__':
                self.run_once()


def _chdir():
    from os import chdir
    # from os.path import abspath, dirname
    from sys import argv
    chdir(dirname(abspath(argv[0])))


def main():
    _chdir()
    app = AppEx('(feh)')
    app.focus()
    app.run_json('data/test.json', 11)


if __name__ == '__main__':
    main()
