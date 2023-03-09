#!/usr/bin/env python3

from plater3d.slicers import cura5
import argparse

def clean_settings(settings):
    dup_allow = set() # settings for which duplicates don't mean override
    disable = set(["day", "time"]) # settings which should be commented out

    already_seen = set()
    out = []
    for scope, k, v in reversed(settings):
        action = None

        if k in disable:
            action = "disable"
        elif k not in dup_allow:
            s = (scope, k)
            if s in already_seen:
                action = "duplicate"
            else:
                action = "ok"
                already_seen.add((scope, k))
        else:
           action = "ok"

        assert action is not None
        out.append((action, (scope, k, v)))

    return list(reversed(out))

def write_settings(settings, filename):
    with open(filename, "w") as f:
        last_scope = None
        for action, (scope, k, v) in settings:
            if last_scope != scope:
                print(f"################## scope: {scope}", file=f)
                last_scope = scope

            if action == "disable" or action == "duplicate":
                print(f"#{action}: {k}=\"{v}\"", file=f)
            else:
                print(f"{k}=\"{v}\"", file=f)

def read_settings_log(sf, firstline, markerpos, marker):
    out = [firstline[p+len(marker)-2:].strip()]

    # every cura setting has a k="v" format in the log file
    in_str = out[-1][-1] != '"'
    stook = False
    while in_str:
        try:
            l = next(sf)
        except StopIteration:
            break

        l = l.strip()
        out.append(r"\n" + l[markerpos:])
        in_str = l[-1] != '"'
        stook = "Slicing took" in l
        #print(in_str, stook, l[-1], out[-1], out[-2])
        assert not stook
    #print("")
    return "".join(out)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse the CuraEngine output and extract settings actually used")

    p.add_argument("logfile", help="Log file (or output) of CuraEngine")
    p.add_argument("output", nargs="?", help="File to store settings in, suitable for diff_cura_settings, as well as -s of printplate")
    args = p.parse_args()

    settings = []
    with open(args.logfile, "r") as f:
        for l in f:
            marker = "[WARNING]  -s"
            p = l.find(marker)
            if p != -1:
                settings.append(read_settings_log(f, l, p, marker))

    if len(settings):
        print(f"Found {len(settings)}, processing last one")

        config = cura5.CURA5Config(None, False)
        settings = config._parse_cli(settings[-1])
        csettings = clean_settings(settings)
        if args.output:
            write_settings(csettings, args.output)
            print(f"Wrote output to {args.output}")
    else:
        print("No settings found")
