#!/usr/bin/env python
# -*- coding: utf-8 -*-
from json import dumps
from multiprocessing import Process, Manager
from wsgiref import simple_server
from utility import AppEx
from falcon import API


class Task():
    def __init__(self, name, walker, times):
        self.name = name
        self.walker = walker
        self.times = times

    def run(self):
        while self.times:
            self.times = self.times - 1
            if self.walker.name == '__stop__':
                break
            elif self.walker.name == '__reset__':
                # todo
                break
            else:
                self.walker.walk_through()

    def stop(self, force=False):
        self.times = 0
        self.walker.stop = force


class TaskHandler():
    def __init__(self, manager):
        self.tasks = manager.list()
        self.process = None

    def handle_tasks(self):
        if self.process and self.process.is_alive():
            return False
        self.process = Process(target=self._handle_tasks)
        self.process.start()
        return True

    def _handle_tasks(self):
        while self.tasks:
            self.tasks[0].run()
            print(len(self.tasks))
            self.tasks.pop(0)
            print(len(self.tasks))

    def list_tasks(self):
        return [{'name': task.name, 'times': task.times} for task in self.tasks]


class TaskWrapper():
    def __init__(self, name, handler, feh, window):
        self.name = name
        self.handler = handler
        self.feh = feh
        self.window = window

    def on_get(self, req, resp, times):  # post
        print(len(self.handler.tasks))
        if isinstance(times, str):
            times = int(times)
        walker = self.feh.load_walker('data/forging-bonds.json', self.window)
        task = Task('forging-bonds({0})'.format(times), walker, times)
        self.handler.tasks.append(task)
        self.handler.handle_tasks()
        resp.body = dumps(self.handler.list_tasks(), ensure_ascii=False)


class Test():
    def on_get(self, req, resp):
        resp.body = 'Hello, World!'


class Server():
    def __init__(self):
        self.falcon = API()
        self.feh = AppEx('(feh)')
        self.window = None
        self.handler = None

    def start(self):
        self.handler = TaskHandler(Manager())
        self.window = self.feh.window()
        self.feh.focus()
        self.falcon.add_route('/', Test())
        self.falcon.add_route('/events/forging-bonds/{times}',
                              TaskWrapper('forging-bonds', self.handler, self.feh, self.window))
        simple_server.make_server('0.0.0.0', 5000, self.falcon).serve_forever()

    def stop(self):
        pass


def _chdir():
    from os import chdir
    from os.path import abspath, dirname
    from sys import argv
    chdir(dirname(abspath(argv[0])))


def main():
    _chdir()
    Server().start()


if __name__ == '__main__':
    main()
