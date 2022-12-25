import os
import json
from pathlib import Path

class PrintJob:
    def __init__(self, name):
        self.name = name
        self.stlfiles = []
        self.counts = {}
        self._loaded = False
        self.machine = ''
        self.extruders = [0]
        self.print_settings = ''

    @property
    def loaded(self):
        return self._loaded

    @property
    def root(self):
        return self.filename.parent

    def exists(self, stlfile):
        return stlfile in self.counts

    def set_print_params(self, machine, extruder, print_settings):
        self.machine = machine
        self.extruders = [extruder]
        self.print_settings = print_settings

    def remove_model(self, stlfile, count):
        if count > self.counts[stlfile]:
            raise ValueError(f"Can't remove more models than exist")

        self.counts[stlfile] -= count
        if self.counts[stlfile] == 0:
            self.stlfiles.remove(stlfile)
            del self.counts[stlfile]

    def add_model(self, stlfile, count):
        if stlfile not in self.counts:
            self.stlfiles.append(stlfile)
            self.counts[stlfile] = count
        else:
            self.counts[stlfile] += count

        return self.counts[stlfile]

    def save(self, filename = None):
        if filename is None:
            filename = self.filename

        if not filename:
            raise ValueError(f"Require filename")

        op = {'name': self.name,
              'version': 1,
              'stlfiles': self.stlfiles,
              'counts': self.counts,
              'machine': self.machine,
              'extruders': self.extruders,
              'print_settings': self.print_settings}

        with open(filename, "w") as f:
            json.dump(op, fp=f, indent='  ')

    @staticmethod
    def load(filename):
        with open(filename, "r") as f:
            op = json.load(fp=f)

        if op.get('version', 0) != 1:
            raise ValueError(f"{filename} is unrecognized as a job file")

        pj = PrintJob(op['name'])
        if len(op.get('extruders', [])) > 1:
            raise NotImplementedError(f"Multiple extruders not supported")

        pj.set_print_params(op.get('machine',''),
                            op.get('extruders', [0])[0],
                            op.get('print_settings', ''))

        for s in op['stlfiles']:
            pj.add_model(s, op['counts'][s])

        pj._loaded = True
        pj.filename = Path(filename)
        return pj

    @staticmethod
    def load_if_exists(name, filename):
        if os.path.exists(filename):
            return PrintJob.load(filename)
        else:
            pj = PrintJob(name)
            pj.filename = Path(filename)
            return pj

    @staticmethod
    def name2file(name):
        return Path(f"{name}.job/printjob.json")
