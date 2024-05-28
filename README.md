# Plater CLI

A command-line tool, `pj3d`, to pack and plate 3D models for 3D
printing. Invokes the Cura slicer from the command line to produce
Gcode files without using the UI.

Although this software has been used to print parts for several 3D
printers now, it is still quite rough and has only been tested with
the Cura 5 AppEngine on Linux.

## Installation

First install the pre-requisites:

```
pip3 install -r requirements.txt
```

Including `stlinfo`, from [here](https://github.com/sree314/stlinfo)

Then, to install this package, run:

```
python3 setup.py develop --user
```

You can replace `develop` with `install` if you don't intend to modify
the source code.

To check installation, run the `pj3d` command.

```
$ pj3d
usage: pj3d [-h] jobname ...
[elided]
```

You should also be able to run `CuraEngine` as follows:

```
$ CuraEngine

Cura_SteamEngine version 5.0.0
Copyright (C) 2022 Ultimaker

...
```

If `CuraEngine` doesn't work, see the section on [CuraEngine setup](#curaengine-setup).

Now, if this is the first time you're running `pj3d`, you need to:

  - [Create a configuration file](#creating-a-configuration-file),
  - [Create a print settings file](#creating-a-print-settings-file)


## Quick Usage Demonstration

First, create a job (change the printer name and settings file as appropriate):

```
pj3d test create "Voron 0" /path/to/voron_print_settings.txt
```

This creates a `test.job` directory that will contain all the
information about this print job.

Then, add models:

```
pj3d test add /path/to/file1.stl
pj3d test add /path/to/file2.stl
```

Pack the models into plates:
```
pj3d test pack
```

Visualize the packings, if needed:
```
pj3d test vispack
```

Print to obtain Gcode:
```
pj3d test print
```

View the Gcode statistics:
```
pj3d test gstats
```

Now, you can print the `.gcode` files in `test.job/*.gcode` by
uploading them to your printer.

You can delete the `test.job` directory after you're done.


## Creating a configuration file

`pj3d` requires a configuration file to obtain some printer
parameters. This file is usually `~/.config/pj3d/pj3d.cfg` on
Unix-like systems. You can view the configuration path being used on
your system using the `config` command:

```
$ pj3d nulljob config
Using config file: /path/to/.config/pj3d/pj3d.cfg
```

If it doesn't exist, you should create this file with a section for
each printer. The name of the section is the name of the printer in
Cura.  The `name` and `mesh` parameters are optional.

```
[Voron 0]
name="Voron 0"
volxyz=120,120,120
mesh=/path/to/voron0_120_bed.stl
```

You can also specify slicer parameters using a section like so:
```
[slicer:cura5]
appimage=true
binary=/path/to/CuraEngine
```

By default, `appimage` is `true` on Linux systems, and `false` on other systems. If the path to `CuraEngine` is not provided, then it must be in your `PATH`.


## Creating a print settings file

To produce the `.gcode` file, the slicer must be passed a list of
settings such as printing temperature, wall widths, etc. In the Cura
GUI, this is usually set as part of the profile. Rather than
reimplement Cura's profile parsing and settings management logic,
`pj3d` works with a print settings file.

The process to obtain a print settings file is a bit
convoluted. First, locate the Cura log file which is usually stored in
`~/.local/share/cura/VERSION/cura.log`. Then, open the Cura GUI, and
slice a model using the preferred settings. To obtain a print settings
file that `pj3d` can use, run the `parse_cli.py` command:

```
$ parse_cli.py /path/to/cura.log /path/to/print_settings.txt
Found 52, processing last one
Wrote output to /path/to/print_settings.txt
```

If you examine this file, you should see the settings that Cura passes
to `CuraEngine`.

You can use this settings file whenever you run `pj3d create`.

## CuraEngine Setup

The `pj3d print` command invokes `CuraEngine` to generate `.gcode`
files from the STL models. If `CuraEngine` does not work, and you're
using a recent version of Cura (5.2.2 and newer, but newer versions such as 5.7 use a different `AppRun` and won't work anymore), try:

```
ln -sf /path/to/Ultimaker-Cura-5.2.2-linux.AppImage ~/.local/bin/CuraEngine
```

You can replace `~/.local/bin` with any folder in your `PATH`.

## Copyright

The contents of this repository are Copyright (c) 2022, 2023, 2024, Sreepathi Pai.

Licensed under the GNU Lesser GPL Public License V3 or later.

