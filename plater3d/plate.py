#!/usr/bin/env python3

import json

class Part:
    def __init__(self, name, index, group, position):
        self.name = name
        self.index = index
        self.group = group
        self.position = position

    def to_dict(self):
        return {'name': self.name,
                'index': self.index,
                'group': self.group,
                'position': self.position}

    @property
    def x(self):
        return self.position[0]

    @x.setter
    def x(self, newx):
        self.position[0] = newx

    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, newy):
        self.position[1] = newy

    @property
    def w(self):
        return self.position[2]

    @property
    def h(self):
        return self.position[3]

    @staticmethod
    def from_dict(d):
        return Part(**d)

# for now, this is read only
class Plate:
    def __init__(self):
        self.parts = []
        self.bounds = []

    def add_part(self, p):
        self.parts.append(p)

    def set_bounds(self, minx, miny, maxx, maxy):
        self.bounds = [minx, miny, maxx, maxy]

    def to_dict(self):
        return {"parts": [p.to_dict() for p in self.parts],
                "bounds": self.bounds}

    @staticmethod
    def from_dict(d):
        plt = Plate()
        for p in d['parts']:
            plt.add_part(Part.from_dict(p))

        plt.set_bounds(*d['bounds'])
        return plt

# readonly for now
class PlatesFile:
    def __init__(self):
        self.plates = []
        self.stlinfo = {}
        self.border = 0
        self.volxyz = None
        self.max_height_diff = 0
        self.platefile = None

    def add_plate(self, plate):
        self.plates.append(plate)

    @staticmethod
    def load(platefile):
        with open(platefile, "r") as f:
            plate = json.load(fp=f)

        if plate.get('type', None) != 'plate':
            raise ValueError(f"{platefile} does not appear to contain a plate")

        out = PlatesFile()
        out.stlinfo = plate['stlinfo']
        out.border = plate['border']
        out.volxyz = plate['volxyz']
        out.max_height_diff = plate['max_height_diff']
        out.platefile = platefile

        for p in plate['plates']:
            P = Plate.from_dict(p)
            out.add_plate(P)

        return out

    def save(self, platefile = None):
        if platefile is None:
            platefile = self.platefile

        assert platefile is not None

        out = {'type': 'plate',
               'stlinfo': self.stlinfo,
               'border': self.border,
               'volxyz': self.volxyz,
               'max_height_diff': self.max_height_diff,
               'plates': [p.to_dict() for p in self.plates]
        }

        with open(platefile, "w") as f:
            json.dump(out, fp=f, indent='  ')
