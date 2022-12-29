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

    def add_plate(self, plate):
        self.plates.append(plate)

    @staticmethod
    def load(platefile):
        with open(platefile, "r") as f:
            plate = json.load(fp=f)

        if plate.get('type', None) != 'plate':
            raise ValueError(f"{platefile} does not appear to contain a plate")

        out = PlatesFile()
        for p in plate['plates']:
            P = Plate.from_dict(p)
            out.add_plate(P)

        return out
