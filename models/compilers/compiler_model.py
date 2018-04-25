#!/usr/bin/env python3

import subprocess
import os

class CompilerModel(object):

    def __init__(self):
        self.name=''
        self.version=''
        self.frontend_name=''
        self.default_flags=''
        self.default_dependencies=[]

    def check(self, bin_path):
        print('I AM CHECKING RIGHT NOW for %s with %s'%( self.frontend_name,
              bin_path))
        if os.path.isdir(bin_path):
            for file in os.listdir(bin_path):
                if file == self.frontend_name:
                    output = subprocess.check_output([os.path.join(bin_path,file),
                                             '--version'])
                    if output.decode('utf-8').find(self.version) != -1:
                        return True
                    else:
                        return False
            return False

    def _fetch_dependencies(self):
        pass

    def _fetch_flags(self, compiling_mode):
        return self.default_flags

    def main(self, compiling_mode):
        self._fetch_dependencies()
        return self._fetch_flags(compiling_mode)
