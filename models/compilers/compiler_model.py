#!/usr/bin/env python3

import subprocess
import os


class CompilerModel(object):

    def __init__(self):
        self.name = ''
        self.version = ''
        self.frontend_name = ''
        self.default_flags = ''
        self.default_dependencies = []

    def check(self, bin_path):
        if os.path.isdir(bin_path):
            for file in os.listdir(bin_path):
                if file == self.frontend_name:
                    output = subprocess.check_output([os.path.join(bin_path, file),
                                                      '--version'])
                    if output.decode('utf-8').find(self.version) != -1:
                        self.frontend_path = os.path.abspath(
                            os.path.join(bin_path, file))
                        return True
                    else:
                        return False
            return False

    def _fetch_dependencies(self):
        pass

    def validate_flags(self, complete_compiler_flags, complete_link_flags):
        '''Translate flags that need to be translated from GNU notation to
           proprietary/exotic notation'''
        return complete_compiler_flags, complete_link_flags

    def _fetch_flags(self, compiling_mode):
        '''Handle Compiling Mode here'''
        compiling_mode_flags = ''
        return self.default_flags + compiling_mode_flags

    def main(self, compiling_mode):
        self._fetch_dependencies()
        return self._fetch_flags(compiling_mode)
