#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
from keyboard import send
from utility import AppEx


def teamviewer():
    while True:
        print('check teamviewer')
        viewer = AppEx('Sponsored session')
        if viewer.isValid():
            viewer.focus()
            send('enter')
        sleep(5)


def _chdir():
    from os import chdir
    from os.path import abspath, dirname
    from sys import argv
    chdir(dirname(abspath(argv[0])))


def main():
    _chdir()
    teamviewer()


if __name__ == '__main__':
    main()
