#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This class is an implementation of the BenchmarkModel interface
    (a python way of doing it, without decorations)

    It implements the actions necessary to prepare for the build, build,
    prepare for the run and run Dr. Ryutaro Himeno's benchmark.

"""

from models.benchmarks.BenchmarkModel import BenchmarkModel
from executor.Execute import OutputParser
import os

class HimenoParser(OutputParser):
    """All data generated by himeno as well as external dictionary"""

    def __init__(self):
        super().__init__()
        self.fields = {
            'mimax': r'\bmimax\b\s+=\s+(\d+)',
            'mjmax': r'\bmjmax\b\s+=\s+(\d+)',
            'mkmax': r'\bmkmax\b\s+=\s+(\d+)',
            'imax': r'\bimax\b\s+=\s+(\d+)',
            'jmax': r'\bjmax\b\s+=\s+(\d+)',
            'kmax': r'\bkmax\b\s+=(\d+)',
            'cpu': r'cpu\s+:\s+(\d+[^\s]*)',
            'Gosa': r'Gosa\s+:\s+(\d+[^\s]*)',
            'MFLOPS': r'MFLOPS measured\s+:\s+(\d+.\d+)',
            'Score': r'Score based on MMX Pentium 200MHz\s+:\s+(\d+.\d+)'
        }


class ModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""

    def __init__(self):
        super().__init__()

        self.name = 'himeno'
        self.executable = 'bmt'
        self.benchmark_url = 'http://accc.riken.jp/en/wp-content/uploads/sites/2/2015/07/himenobmt.c.zip'
        self.size = 2
        # As seen below, we need to change the type size to double to get repeatable
        # results, but that also doubles the size of BSS, which needs a larger
        # memory model on x86_64 (but not on AArch64)
        self.compiler_flags = '-mcmodel=large'

    def prepare(self, root_path, compilers_dict, iterations, size):
        super().prepare(root_path, compilers_dict, iterations, size)

        # Himeno specific flags based on options
        # Validation will need more stable execution
        if (self.size >= 3):
            self.checks = {'Gosa': lambda x: x == '7.394327e-04'}
            self.make_flags += 'MODEL=LARGE'
        elif (self.size == 2):
            self.checks = {'Gosa': lambda x: x == '1.244771e-03'}
            self.make_flags += 'MODEL=MIDDLE'
        else:
            self.checks = {'Gosa': lambda x: x == '1.688138e-03'}
            self.make_flags += 'MODEL=SMALL'

        # Download the benchmark, unzip
        prepare_cmds = []
        prepare_cmds.append(['mkdir', self.root_path])
        prepare_cmds.append(['wget',
                             '-P', self.root_path,
                             self.benchmark_url])
        prepare_cmds.append(['unzip',
                             os.path.join(self.root_path, 'himenobmt.c.zip'),
                             '-d', self.root_path])
        prepare_cmds.append(['lhasa', '-xw=' + self.root_path,
                             os.path.join(self.root_path, 'himenobmt.c.lzh')])
        # Himeno uses a lot of floating point multiplication and accumulation
        # which causes a lot of precision issues with float types. Using double
        # also saves a few instructions on 64-bit machines, but halves the lanes
        # for vector instructions. Penalty is about 25% on average.
        prepare_cmds.append(['sed', '-i', 's/float/double/g',
                             os.path.join(self.root_path, 'himenoBMT.c')])
        return prepare_cmds

    def get_plugin(self):
        """Returns the plugin to parse the results"""
        return HimenoParser()
