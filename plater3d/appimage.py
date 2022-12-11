import subprocess
import os

class AppImage2:
    def __init__(self, appimage):
        self.appimage = appimage
        self._process = None

    def mount(self):
        if self._process is None:
            self._process = subprocess.Popen([self.appimage, "--appimage-mount"], bufsize = 0, stdout = subprocess.PIPE)

            d = b''
            while True:
                d1 = os.read(self._process.stdout.fileno(), 256)
                if len(d1):
                    d += d1
                    if b'\n' in d1: break

            self.mount_path = d[:d.index(b'\n')].decode('utf-8')
            print(self.mount_path, self._process)

    def unmount(self):
        if self._process is not None:
            self._process.stdout.close()
            self._process.terminate()
            self._process.wait()
            self._process = None
