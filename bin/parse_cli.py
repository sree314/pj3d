#!/usr/bin/env python3

from plater3d.slicers import cura5
import argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse the CuraEngine output and extract settings actually used")

    p.add_argument("logfile", help="Log file (or output) of CuraEngine")
    p.add_argument("output", nargs="?", help="Debug output, suitable for diff_cura_settings")
    args = p.parse_args()

    settings = []
    with open(args.logfile, "r") as f:
        for l in f:
            marker = "[WARNING]  -s"
            p = l.find(marker)
            if p != -1:
                settings.append(l[p+len(marker)-2:])

    if len(settings):
        print(f"Found {len(settings)}, processing last one")

        config = cura5.CURA5Config(None, False)
        config._parse_cli(settings[-1], args.output)
    else:
        print("No settings found")
