#!/usr/bin/env python3

import os
import argparse
import subprocess
import re
import importlib
from pathlib import Path
from helper.compiler_factory import CompilerFactory
from models.compilers.compiler_model import CompilerModel
from models.benchmarks.benchmark_model import BenchmarkModel
from models.machines.machine_model import MachineModel

class BenchmarkController(object):
    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args

    def _load_benchmark_model(self, benchmark_name):
        mod = importlib.import_module('models.benchmarks.' + benchmark_name)
        return mod.BenchmarkModelImplementation()

    def _load_machine_model(self, machine_type):
        mod = importlib.import_module('models.machines.' + machine_type)
        return mod.MachineModelImplementation()

    def _validate_model(self, model_name, model_type):
        filename = 'models/'+ model_type + 's/' + model_name + '.py'
        if os.path.isfile(filename):
            raw = Path(filename).read_text()
            if model_type == 'benchmark':
                if raw.find('class BenchmarkModelImplementation') == -1:
                    raise ImportError('Cannot find class BenchmarkModelImplementation in '
                                  + filename)
                else:
                    return self._load_benchmark_model(model_name)
            elif model_type == 'machine':
                if raw.find('class MachineModelImplementation') == -1:
                    raise ImportError('Cannot find class MachineModelImplementation in '
                                  + filename)
                else:
                    return self._load_machine_model(model_name)
        else:
            raise ImportError('Cannot find plugin ' + filename)

    def main(self):
        subprocess.check_output(['mkdir', self.args.benchmark_root + self.args.name])
        subprocess.check_output(['mkdir', self.args.benchmark_root + self.args.name +
                                 '/compiler'])
        subprocess.check_output(['mkdir', self.args.benchmark_root + self.args.name +
                                 '/benchmark'])

        try:
            self.benchmark_model = self._validate_model(self.args.name +
                                                        '_model', 'benchmark')
        except ImportError as err:
            print(err)
            self.parser.print_help()

        try:
            self.machine_model = self._validate_model(self.args.machine_type +
                                                      '_model', 'machine')
        except ImportError as err:
            print(err)
            self.parser.print_help()

        compiler_factory = CompilerFactory(self.args.toolchain_url, self.args.benchmark_root +
                                          self.args.name + '/benchmark/')

        try:
            self.compiler_model = compiler_factory.getCompiler()
        except ImportError as err:
            print(err)
            self.parser.print_help()

        self.compiler_model.main('DEFAULT')
        self.machine_model.main()

        self.benchmark_model.run_benchmark(self.args.benchmark_options, "prout")

        identity = str(args.name + '_' + self.compiler_model.frontend_name + '_' + args.compiler_flags.replace(" ", "") +
               '_' + args.machine_type + '_' + args.benchmark_options.replace(" ", "") +
               '_' + args.build_number)
        execname = re.sub("[^a-zA-Z0-9_]+", "", identity).lower()
        report_name = identity + '.report'




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run some benchmark.')
    parser.add_argument('name', metavar='benchmark_name', type=str,
                    help='The name of the benchmark to be run')
    parser.add_argument('machine_type', type=str,
                    help='The type of the machine to run the benchmark on')
    parser.add_argument('toolchain_url', type=str,
                    help='The url of the toolchain with which to compile the benchmark')
    parser.add_argument('--compiler-flags', type=str, default='',
                    help='The compiler flags to use with compiler')
    parser.add_argument('--benchmark-options', type=str, default='',
                    help='The benchmark options to use with the benchmark')
    parser.add_argument('--benchmark-root', type=str,
                    help='The benchmark root directory where things will be \
                        extracted and created')
    parser.add_argument('--build-number', type=str, required=True,
                    help='The number of the benchmark run this is')
    args = parser.parse_args()

    controller = BenchmarkController(parser, args)
    controller.main()
