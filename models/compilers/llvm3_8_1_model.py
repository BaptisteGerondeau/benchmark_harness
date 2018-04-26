#!/usr/bin/env python3

from models.compilers.compiler_model import CompilerModel

class CompilerModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name='llvm'
        self.version='3.8.1'
        self.frontend_name='clang'
        self.default_flags='-O3 -ffast-math -ffp-contract=on'
        self.default_dependencies=[]