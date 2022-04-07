import sys
import subprocess
import re
import shutil
import os
import signal

def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', folder, source]

    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        outs, errs = process.communicate(timeout=timeout)

        filename = re.search('-> (.*?) using filter', outs.decode())
        if filename is None:
            raise LibreOfficeError(outs.decode())
        else:
            return filename.group(1)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        raise

def libreoffice_exec():
    if sys.platform.startswith('linux'):
        # Linux specific code here ...
        return shutil.which("soffice")
    elif sys.platform.startswith('darwin'):
        # OSX specific code here ...
        return 'osx'
    else:
        return 'libreoffice'

class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output

if __name__ == '__main__':
    print(libreoffice_exec())
    print('Converted to ...')
    convert_to(sys.argv[1], sys.argv[2], timeout=20)

