#!/usr/bin/env python
# -*- coding: utf-8 -*-
from json import dumps
from multiprocessing import Process, Pipe
from wsgiref import simple_server
from falcon import API
from utility import AppEx


class Task():
    def __init__(self, name, walker, times):
        self.name = name
        self.walker = walker
        self.times = times

    def run(self, out_connection):
        out_connection.send({'times': self.times})
        while self.times:
            print()
            print(self.name, self.times)
            print()
            self.times = self.times - 1
            out_connection.send({'times': self.times})
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
    def __init__(self):
        self.tasks = []
        self.process = None
        self.parent_send_connection, self.child_recv_connection = Pipe()
        self.parent_recv_connection, self.child_send_connection = Pipe()

    def handle_tasks(self):
        if self.process and self.process.is_alive():
            return False
        args = [self.child_recv_connection, self.child_send_connection]
        self.process = Process(target=self._handle_tasks, args=args)
        self.process.start()
        return True

    def _handle_tasks(self, in_connection, out_connection):
        while self.tasks:
            if in_connection.poll():
                message = in_connection.recv()
                task = message.get('task')
                if task:
                    self.tasks.append(task)
                elif message.get('stop', False):
                    break
            self.tasks[0].run(out_connection)
            self.tasks.pop(0)

    def add_tasks(self, task):
        self.tasks.append(task)
        if not self.handle_tasks():
            self.parent_send_connection.send({'task': task})

    def update_tasks(self):
        while self.parent_recv_connection.poll():
            message = self.parent_recv_connection.recv()
            times = message.get('times', -1)
            if times != -1 and self.tasks:
                self.tasks[0].times = times
            if self.tasks[0].times <= 0:
                self.tasks.pop(0)
        return self.tasks

    def list_tasks(self):
        return [{'name': task.name, 'times': task.times} for task in self.update_tasks()]

    def on_get(self, _, resp):
        resp.body = dumps(self.list_tasks(), ensure_ascii=False)


class TaskWrapper():
    def __init__(self, name, server):
        self.name = name
        self.server = server

    def on_post(self, _, resp, times):  # post
        if isinstance(times, str):
            times = int(times)
        feh = self.server.feh
        window = self.server.window
        handler = self.server.handler
        walker = feh.load_walker('data/forging-bonds.json', window)
        name = 'forging-bonds({0})'.format(times)
        task = Task(name, walker, times)
        handler.add_tasks(task)
        resp.body = dumps(handler.list_tasks(), ensure_ascii=False)

    def on_get(self, req, resp, times):
        self.on_post(req, resp, times)


class Server():
    def __init__(self):
        self.falcon = API()
        self.feh = AppEx('(feh)')
        self.window = None
        self.handler = None

    def start(self):
        self.feh.focus()
        self.window = self.feh.window()
        print(self.window.getW(), self.window.getH())
        self.handler = TaskHandler()
        self.falcon.add_route('/', self.handler)
        forging_bonds = TaskWrapper('forging-bonds', self)
        self.falcon.add_route('/events/forging-bonds/{times}', forging_bonds)
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
