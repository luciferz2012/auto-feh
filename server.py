#!/usr/bin/env python
# -*- coding: utf-8 -*-
from json import dumps
from multiprocessing import Process, Manager
from wsgiref import simple_server
from falcon import API
from utility import AppEx


class Task():
    def __init__(self, name, walker, manager, times):
        self.name = name
        self.walker = walker
        self._times = manager.Value('i', times)

    @property
    def times(self):
        return self._times.value

    @times.setter
    def times(self, times):
        self._times.value = times

    def run(self):
        while self.times:
            print()
            print(self.name, self.times)
            print()
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
        self.manager = manager
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
            self.tasks.pop(0)

    def list_tasks(self):
        return [{'name': task.name, 'times': task.times} for task in self.tasks]

    def on_get(self, _, resp):
        resp.body = dumps(self.list_tasks(), ensure_ascii=False)


class TaskWrapper():
    def __init__(self, name, handler, feh, window):
        self.name = name
        self.handler = handler
        self.feh = feh
        self.window = window

    def on_post(self, _, resp, times):  # post
        if isinstance(times, str):
            times = int(times)
        walker = self.feh.load_walker('data/forging-bonds.json', self.window)
        name = 'forging-bonds({0})'.format(times)
        task = Task(name, walker, self.handler.manager, times)
        self.handler.tasks.append(task)
        self.handler.handle_tasks()
        resp.body = dumps(self.handler.list_tasks(), ensure_ascii=False)

    def on_get(self, req, resp, times):
        self.on_post(req, resp, times)


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
        self.falcon.add_route('/', self.handler)
        self.falcon.add_route('/events/forging-bonds/{times}',
                              TaskWrapper('forging-bonds', self.handler, self.feh, self.window))
        simple_server.make_server('0.0.0.0', 3388, self.falcon).serve_forever()

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
