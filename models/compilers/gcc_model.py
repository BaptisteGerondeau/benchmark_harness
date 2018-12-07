#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.CompilerModel import CompilerModel

class ModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name = 'gcc'
        self.version = ''
        self.cc_name = 'gcc'
        self.cxx_pattern = r'(.*g\+\+-\d+.*)|(.*g\+\+$)'
        self.cc_pattern = r'(.*gcc-\d+.*)|(.*gcc$)'
        self.fc_pattern = r'(.*gfortran-\d+.*)|(.*gfortran$)'
        self.default_compiler_flags = '-O3 -ffast-math -funroll-loops'
