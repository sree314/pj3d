#!/usr/bin/env python3

import platform
import os
from pathlib import Path
import configparser

class Config:
    def __init__(self, path = None):
        if path is None:
            path = get_config_dir() / 'pj3d'

        if not path.exists():
            os.makedirs(path)

        self.configfile = path / 'pj3d.cfg'
        self.config = configparser.ConfigParser()
        if self.configfile.exists():
            self.config.read(self.configfile)

    def _get_for_type(self, type_):
        if type_ is str:
            f = self.config.get
        elif type_ is bool:
            f = self.config.getboolean
        elif type_ is int:
            f = self.config.getint
        elif type_ is float:
            f = self.config.getfloat
        else:
            raise NotImplementedError(f"Unable to support value type {type_}")

        return f

    def get_printer_prop(self, printer, prop, default=None, type_=str):
        return self._get_for_type(type_)(printer, prop, fallback=default)

    def get_prop(self, prop, default=None, type_=str):
        return self._get_for_type(type_)('pj3d', prop, fallback=default)

    def get_slicer_prop(self, slicer, prop, default=None, type_=str):
        f = self._get_for_type(type_)
        return f(f'slicer:{slicer}', prop, fallback=default)

def get_config_dir():
    path = None
    if platform.system() == 'Windows':
        path = os.environ.get('APPDATA', '') or '~/AppData/Roaming'
    else:
        path = os.environ.get('XDG_CONFIG_HOME', '') or '~/.config'

    return Path(os.path.abspath(os.path.expanduser(path)))

def get_appimage_default():
    s = platform.system()
    if s == 'Linux':
        return True
    else:
        return False
