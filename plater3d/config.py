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

    def get_printer_prop(self, printer, prop, default=None):
        return self.config.get(printer, prop, fallback=default)

    def get_prop(self, prop, default):
        return self.config.get('pj3d', prop, fallback=default)

def get_config_dir():
    path = None
    if platform.system() == 'Windows':
        path = os.environ.get('APPDATA', '') or '~/AppData/Roaming'
    else:
        path = os.environ.get('XDG_CONFIG_HOME', '') or '~/.config'

    return Path(os.path.abspath(os.path.expanduser(path)))
