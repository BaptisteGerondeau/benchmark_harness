#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.CompilerModel import CompilerModel

class ModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name = 'clang'
        self.version=''
        self.cc_name='clang'
        self.cc_pattern=r'(.*clang-\d+.*)|(.*clang$)'
        self.cxx_pattern=r'(.*clang\+\+-\d+.*)|(.*clang\+\+$)'
        self.fc_pattern=r'(.*flang-\d+.*)|(.*flang$)'
        self.default_compiler_flags='-O3 -ffast-math -ffp-contract=on'
