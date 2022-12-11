#!/usr/bin/env python3
#
# diff_cura_settings.py
# Compares two settings files to figure out what settings are missing

import argparse
import re

settings_re = re.compile(r'(?P<key>[^ =]+)="(?P<value>.*)"')
num_re = re.compile(r"[0-9]+(\.[0-9]*)?$")

def load(settings_file):
    out = {}

    with open(settings_file, "r") as f:
        for l in f:
            if l[0] == "#": continue
            if l.strip() == '': continue
            m = settings_re.match(l)
            if m:
                k = m.group('key')
                v = m.group('value')
                if k not in out:
                    out[k] = []

                out[k].append(v)
            else:
                raise ValueError(f"Invalid setting: {l}")

    return out

def is_equal(v1, v2):
    if v1 == "False" or v1 == "false":
        return v1.lower() == v2.lower()
    elif v1 == "True" or v1 == "true":
        return v1.lower() == v2.lower()
    elif num_re.match(v1):
        return float(v1) == float(v2)
    else:
        return v1 == v2

def diff(s1, s2, s1name, s2name):
    s1k = set(s1.keys())
    s2k = set(s2.keys())

    only_in_s1 = s1k - s2k
    only_in_s2 = s2k - s1k

    diff = []

    if len(only_in_s1):
        print(f">>>>==== Only in {s1name}")
        for k in only_in_s1:
            print("\t", k, s1[k])
            diff.append((k, s1[k][-1]))

    if len(only_in_s2):
        print(f">>>>==== Only in {s2name}")
        for k in only_in_s2:
            print("\t", k, s2[k])

    in_both = s1k.intersection(s2k)

    same = set()
    for k in in_both:
        if not is_equal(s1[k][-1], s2[k][-1]):
            print(k, s1[k], s2[k])
            diff.append((k, s1[k][-1]))
        else:
            same.add(k)

    return diff

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Compare two (debug) xsettings files")
    p.add_argument("file1")
    p.add_argument("file2")
    p.add_argument("-o", dest="output", help="Output settings file with settings from file1 missing and different from file2")

    args = p.parse_args()

    f1 = load(args.file1)
    f2 = load(args.file2)

    d = diff(f1, f2, args.file1, args.file2)
    if args.output:
        with open(args.output, "w") as f:
            for k, v in d:
                print(f"{k}=\"{v}\"", file=f)

