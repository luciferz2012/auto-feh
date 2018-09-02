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

    @staticmethod
    def handle_images(img_dir, json, region):
        json_width = json.get('width')
        json_height = json.get('height')
        if json_width and json_height:
            region_width = region.getW()
            region_height = region.getH()
            tmp_dir = '{0}_{1}x{2}_tmp'\
                .format(img_dir, region_width, region_height)
            if not exists(tmp_dir):
                mkdir(tmp_dir)
                factor_x = region_width / json_width
                factor_y = region_height / json_height
                factor = min(factor_x, factor_y)
                if factor > 1:
                    factor = factor * 1.01
                elif factor < 1:
                    factor = factor * 0.99
                AppEx.resize_images(img_dir, tmp_dir, factor)
            return tmp_dir
        return img_dir

    @staticmethod
    def load_walker(path, region):
        img_dir = dirname(abspath(path))
        with open(path) as file:
            json = load(file)
            events = json.get('events')
            start = json.get('start')
            if events and start:
                img_dir = AppEx.handle_images(img_dir, json, region)
                return EventWalker(events, start, region, img_dir)
        return None


class EventWalker():
    def __init__(self, events, start, region, img_dir):
        self.events = events
        self.start = start
        self.region = region
        self.img_dir = img_dir
        self.stop = False
        self.name = start
        self.last = '__end__'

    def try_find(self, pattern, wait=0):
        try:
            self.region.setAutoWaitTimeout(wait)
            return self.region.findBest(pattern)
        except FindFailed:
            pass

    def best_match(self, event):
        loop = event.get('__loop__', 1)
        sleep = event.get('__sleep__', 0)
        wait = event.get('__wait__', 3)
        delay = event.get('__delay__', 0)
        max_name = None
        for _ in range(loop):
            max_score = 0
            max_match = None
            max_img = None
            self.region.wait(sleep)
            for key, value in event.items():
                if key.startswith('__') and key.endswith('__'):
                    continue
                match = self.try_find(join(self.img_dir, key), wait)
                if match and match.getScore() > max_score:
                    max_name = value
                    max_score = match.getScore()
                    max_match = match
                    max_img = key
            if max_match:
                self.region.wait(delay)
                if max_name != '__end__':
                    max_match.click()
                print('{0}: {1}({2:.2}) -> {3}'
                      .format(self.name, max_img, max_score, max_name))
            else:
                break
        return max_name

    def walk_once(self):
        event = self.events.get(self.name)
        if event:
            name = self.best_match(event)
            if name == '__last__':
                self.name = self.last
                self.last = '__end__'
            else:
                self.last = self.name
                if name:
                    self.name = name
                else:
                    self.name = event.get('__none__', '__end__')
                    print('{0}: no match -> {1}'.format(self.last, self.name))
        else:
            self.last = self.name
            self.name = '__end__'
            print('{0}: not found'.format(self.last))

    def walk_through(self):
        self.name = self.start
        for _ in range(1024):
            if self.stop:
                self.name = '__stop__'
            if self.name in ['__end__', '__stop__', '__reset__']:
                break
            self.walk_once()


def _chdir():
    from os import chdir
    # from os.path import abspath, dirname
    from sys import argv
    chdir(dirname(abspath(argv[0])))


def main():
    _chdir()
    app = AppEx('(feh)')
    app.focus()
    window = app.window()
    print(window.getW(), window.getH())
    walker = app.load_walker('data/weekly-rival-domains.json', window)
    for _ in range(15):
        walker.walk_through()
        if walker.name == '__stop__':
            break
        elif walker.name == '__reset__':  # todo
            break


if __name__ == '__main__':
    main()
