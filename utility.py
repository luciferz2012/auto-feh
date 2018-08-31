#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lackey import App, FindFailed
from json import load


class AppEx(App):
    def run_json(self, path, times=1, window_index=0):
        with open(path) as file:
            json = load(file)
            events = json.get('events')
            start = json.get('start')
            if events and start:
                for i in range(times):
                    EventHandler(self.window(window_index), 
                                 events, start).run_all()


class EventHandler():
    def __init__(self, region, events, name):
        self.region = region
        self.events = events
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
            wait = event.get('__wait__', 3)
            delay = event.get('__delay__', 0)
            max_name = None
            for i in range(loop):
                max_score = 0
                max_match = None
                for key, value in event.items():
                    if key.startswith('__') and key.endswith('__'):
                        continue
                    match = self.try_find(key, wait)
                    if match:
                        score = match.getScore()
                        if score > max_score:
                            max_score = score
                            max_match = match
                            max_name = value
                if max_match:
                    self.region.wait(delay)
                    max_match.click()
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
    from os.path import abspath, dirname
    from sys import argv
    chdir(dirname(abspath(argv[0])))


def main():
    _chdir()
    app = AppEx('(feh)')
    app.focus()
    app.run_json('test.json', 11)


if __name__ == '__main__':
    main()
