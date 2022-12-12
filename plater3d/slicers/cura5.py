import configparser
import json
from pathlib import Path
from ..appimage import AppImage2
import os
import logging
from collections import namedtuple
from urllib.parse import unquote_plus
import itertools
import re
import subprocess
from ..xform import Rotation3D

# the re that matches as setting
setting_re = re.compile(r'(?P<setting>[^ =]+)="(?P<value>[^"]*)"')

cura_config = namedtuple('cura_config', 'cfg ty')

logger = logging.getLogger(__name__)

class FileSettings:
    def __init__(self, filename):
        self.filename = filename
        self._load_settings()

    def _load_settings(self):
        out = []
        with open(self.filename, "r") as f:
            for l in f:
                if l[0] == "#": continue
                if l.strip() == '': continue
                m = setting_re.match(l)
                if m:
                    k = m.group('setting')
                    v = m.group('value')
                    out.append((k, v))
                else:
                    raise ValueError(f"Invalid setting: {l}")

        self._settings = out

    def get_defs(self):
        return {}

    def get_env(self):
        return {}

    def get_general_settings(self):
        for k, v in self._settings:
            yield ('-s', f"{k}={v}")

    def get_part_settings(self, partndx):
        return {}

class ConfigSettings:
    def __init__(self, config, machine, extruder):
        self.cfg = config
        self.machine = machine
        self.extruder = extruder

        # these are a list of config files containing more info
        self.ms = self.cfg.get_machine_settings(machine)
        self.es = self.cfg.get_extruder_settings(extruder)

        self.mkv, self.mj = self.cfg._load_kv_settings(self.ms)
        self.ekv, self.ej = self.cfg._load_kv_settings(self.es)

    def get_env(self):
        search_path = [self.cfg.installed_resources_root / x for x in ['definitions', 'extruders', 'variants']]

        env = {}
        yield ('CURA_ENGINE_SEARCH_PATH', ":".join([str(s) for s in search_path if s.exists()]))

    def get_defs(self):
        for j in itertools.chain(self.mj, self.ej):
            yield ('-j', str(j))

    def get_general_settings(self):
        for k, v in itertools.chain(self.ekv.items(), self.mkv.items()):
            yield ('-s', f"{k}={v}")

    def get_part_settings(self, partndx):
        return {}

class CURA5Config:
    """Locate CURA 5.0 configuration files"""
    def __init__(self, binary, appimage = False):
        self.binary = binary
        self.appimage = appimage
        self._ai = None

    def __del__(self):
        if self._ai:
            self._ai.unmount()
            self._ai = None

    def load_native_config(self):
        self.user_config = Path(os.path.expanduser('~/.config/cura/5.0/'))
        self.local_share = Path(os.path.expanduser('~/.local/share/cura/5.0/'))

        if self.appimage:
            if not self._ai:
                self._ai = AppImage2(self.binary)
                self._ai.mount()
                self.installed_resources_root = Path(self._ai.mount_path) / 'share' / 'cura' / 'resources'
        else:
            raise NotImplementedError(f"Non-AppImage installs not supported")

        self._load_all_configs(self.local_share)
        self._load_machines()
        self._load_extruders()

    def _load_all_configs(self, lspath):
        if not lspath.exists(): return
        logger.info(f'Searching for configs in {lspath}')

        # filename -> config
        self._configs = {}

        # name -> list[filenames]
        self._names2configs = {}

        # basename -> filename
        self._cfgfn2configs = {}

        for c in (lspath).glob('**/*.cfg'):
            cfg = configparser.ConfigParser()
            cfg.read(c)

            csuf = c.name.rsplit('.', 2)
            assert csuf[0] not in self._cfgfn2configs, f"Duplicate config filename: {csuf}"

            self._cfgfn2configs[unquote_plus(csuf[0])] = c

            mdv = cfg.get('metadata', 'setting_version')
            if mdv == "20":
                ty =  cfg.get('metadata', 'type')
                self._configs[c] = cura_config(cfg=cfg, ty=ty)

                n = cfg.get('general', 'name')
                if n in self._names2configs:
                    if ty == 'quality_changes':
                        cq = cfg.get('metadata', 'quality_type')
                        if cq == 'draft':
                            logger.warning(f"{c}: Ignoring draft quality '{n}'")
                        else:
                            nn = []
                            for oldc in self._names2configs[n]:
                                oldcfg = self._configs[oldc].cfg
                                oq = oldcfg.get('metadata', 'quality_type')

                                if oq == 'draft':
                                    logger.warning(f"{oldc}: Ignoring draft quality '{n}'")
                                else:
                                    nn.append(oldc)

                            nn.append(c)
                            self._names2configs[n] = nn
                    else:
                        logger.warning(f"{c}: Duplicate name {n} , overwriting old from {self._names2configs[n]}")
                        self._names2configs[n] = [c]
                else:
                    self._names2configs[n] = [c]
            else:
                log.warning(f"{c}: Unsupported metadata version {mdv}")

        #logger.debug(f"name2configs: {self._names2configs}")
        #logger.debug(f"cfgfn2configs: {self._cfgfn2configs}")


    def _load_machines(self):
        # machine name -> config
        self._machines = {}
        if self._configs:
            for v in self._configs.values():
                if v.ty == "machine":
                    # also has id, but unsure why
                    self._machines[v.cfg.get('general', 'name')] = v

    def _load_extruders(self):
        # machine name -> config
        self._extruders = {}
        self._mac2extruders = {}
        if self._configs:
            for v in self._configs.values():
                if v.ty == "extruder_train":
                    # also has id, but unsure why
                    name = v.cfg.get('general', 'name')
                    self._extruders[name] = v
                    machine = v.cfg.get('metadata', 'machine')
                    if machine not in self._mac2extruders:
                        self._mac2extruders[machine] = []

                    self._mac2extruders[machine].append(name)

    def load_from_installed(self, stem):
        out = []
        #TODO: note that extruder setting are .inst.cfg
        for c in self.installed_resources_root.glob(f"**/{stem}.def.json"):
            out.append(c)

        return out

    def _load_kv_settings(self, settings):
        out = {}
        defjsons = []
        for s in settings:
            if s in self._configs:
                for k in self._configs[s].cfg["values"]:
                    #print(s, k)
                    out[k] = self._configs[s].cfg["values"][k]
            else:
                defjsons.append(s)
                print("!!", s)

        return out, defjsons

    def invoke_slicer(self, machine, extruder_ndx, settings, parts, output):
        extruders = self._mac2extruders[machine]
        kvx = {'machine_extruder_count': len(extruders),
               'adhesion_extruder_nr': extruder_ndx}

        # order matters, later settings take precedence
        cmd = [self.binary, "slice"]

        env = dict(itertools.chain(*map(lambda x: x.get_env(), settings)))

        # first definitions
        for flag in itertools.chain(*map(lambda x: x.get_defs(), settings)):
            cmd.extend(flag)

        for flag in itertools.chain(*map(lambda x: x.get_general_settings(), settings)):
            cmd.extend(flag)

        for k, v in kvx.items():
            cmd.extend(('-s', f'{k}={v}'))

        for p in parts:
            if p.rotation is not None:
                rot = Rotation3D(*p.rotation)
                cmd.extend(['-s', f'mesh_rotation_matrix={rot.matrix()}'])

            cmd.extend(['-l', p.filename])

            if p.offset is None:
                # TODO: add center_object here?
                pass
            else:
                for pos, off in zip(('x', 'y', 'z'), p.offset):
                    # absolute pos or offset?
                    cmd.extend(['-s', f'mesh_position_{pos}={off}'])



        cmd.extend(['-o', output])

        print(" ".join([f'{k}={v}' for (k, v) in env.items()]),
              " ".join(cmd))

        if not dry_run:
            with open("invoke.log", "w") as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, check=True)
            #print(output.decode('utf-8', errors='replace'), file=f)
            #print(output)

    def _load_container(self, name, ccfg):
        settings = []
        for o in ccfg['containers']:
            v = ccfg['containers'][o]
            if v in self._names2configs:
                settings.extend(self._names2configs[v])
            elif v.startswith('empty_'):
                pass
            elif v in self._cfgfn2configs:
                settings.append(self._cfgfn2configs[v])
            else:
                print("Trying to load", v)
                vs = self.load_from_installed(v)
                if len(vs):
                    settings.extend(vs)
                else:
                    logger.warning(f"{name}: Container {v} not found!")

        return settings

    def get_extruder_settings(self, extruder):
        return self._load_container(extruder, self._extruders[extruder].cfg)

    def get_machine_settings(self, machine):
        return self._load_container(machine, self._machines[machine].cfg)

    def _parse_cli(self, cmdline, settings_file = None):
        # patch up breaks on "
        cmdline = cmdline.replace("\n", " ").split(' ')
        out_cmdline = []
        in_string = False
        for c in cmdline:
            if in_string:
                out_cmdline[-1] += " " + c
            else:
                out_cmdline.append(c)

            p = c.find('"')
            if p != -1:
                if in_string:
                    in_string = False
                else:
                    p2 = c.find('"', p + 1)
                    if p2 == -1:
                        in_string = True

        assert not in_string, f"Unterminated string in {settings_file}"

        last_scope = ("general", 0)
        group_id = 0
        object_id = 0
        oci = iter(out_cmdline)
        settings = []
        while True:
            try:
                o = next(oci)
            except StopIteration:
                break

            if o == "-g":
                last_scope = ("group", group_id)
                group_id += 1
            elif o == "--next":
                last_scope = ("group", group_id)
            elif o == "-l":
                obj = next(oci)
                last_scope = ("object", object_id)
                object_id += 1
            elif o[:2] == "-e":
                last_scope = ("extruder", int(o[2:]))
            elif o == "-v" or o == "-p" or o[:2] == "-m":
                pass
            elif o == "-o":
                ofile = next(oci)
            elif o == '':
                pass
            elif o == "-s":
                s = next(oci)
                m = setting_re.match(s)
                if not m:
                    raise ValueError(f"Setting {s} does not match settings_re")

                settings.append((last_scope, m.group('setting'), m.group('value')))
            else:
                raise NotImplementedError(f"Command line option {o}")

        if settings_file:
            last_scope = None
            with open(f'debug_{settings_file}', 'w') as f:
                for scope, k, v in settings:
                    if last_scope != scope:
                        print(f"################## scope: {scope}", file=f)
                        last_scope = scope
                    print(f"{k}=\"{v}\"", file=f)

        return settings

    # def load_settings_from_file(self, settings_file):
    #     # the settings file contains a CLI invocation
    #     #   Usually, is actually from the CURA logs that shows the backend output
    #     #   but also from the debug messages that CuraEngine prints
    #     with open(settings_file, "r") as f:
    #          # without CuraEngine slice
    #         cmdline = f.read()
    #         return self._parse_cli(cmdline, settings_file)

    def load_settings_from_file(self, settings_file):
        return FileSettings(settings_file)

    def load_settings_from_config(self, machine, extruder):
        return ConfigSettings(self, machine, extruder)

    def serialize(self):
        cfg = {'type': 'cura5',
               'appimage': self.appimage,
               }

        return {self.binary: cfg}

    def deserialize(self, config):
        if binary in config:
            assert config['type'] == 'cura5', f'{self.binary} configuration is not "cura5", is {config["type"]}'
            self.appimage = config['appimage']

class CURA5:
    def __init__(self):
        pass
