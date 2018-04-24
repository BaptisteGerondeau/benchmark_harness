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
