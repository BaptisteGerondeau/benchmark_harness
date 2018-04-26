#!/usr/bin/env python3

import os
import argparse
import subprocess
import re
import importlib
import yaml
from pathlib import Path
from helper.cd import cd
from helper.compiler_factory import CompilerFactory
from models.compilers.compiler_model import CompilerModel
from models.benchmarks.benchmark_model import BenchmarkModel
from models.machines.machine_model import MachineModel
from executor.execute import run
from executor.linux_perf import *


class BenchmarkController(object):
    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args

    def _make_unique_name(self):
        identity = str(
            self.args.name +
            '_' +
            (self.args.toolchain_url.rsplit('/', 1)[-1])[:24] +
            '_' +
            self.args.compiler_flags.replace(
                " ",
                "") +
            '_' +
            self.args.machine_type +
            '_' +
            self.args.benchmark_options.replace(
                " ",
                ""))
        self.binary_name = re.sub("[^a-zA-Z0-9_]+", "", identity).lower()
        self.report_name = identity + '.report'

    def _build_complete_flags(self):
        if self.compiler_model is not None and self.benchmark_model is not None \
                and self.machine_model is not None:
            complete_build_flags, complete_link_flags = self.compiler_model.main(
                'DEFAULT')
            m_complete_build_flags, m_complete_link_flags = self.machine_model.main()
            b_complete_build_flags, b_complete_link_flags = self.benchmark_model.fetch_flags()

            complete_build_flags = complete_build_flags + ' ' + m_complete_build_flags + \
                 ' ' +b_complete_build_flags +  ' ' + self.args.compiler_flags

            complete_link_flags = complete_link_flags +  ' ' +m_complete_link_flags + \
                 ' ' +b_complete_link_flags +  ' ' +self.args.link_flags

            complete_build_flags, complete_link_flags = self.compiler_model.validate_flags(
                complete_build_flags, complete_link_flags)

            return complete_build_flags, complete_link_flags

    def _output_logs(self, stdout, perf_results):
        result_dir = self.args.benchmark_root + self.binary_name + '/results'
        if stdout and not isinstance(stdout, str):
            raise TypeError('stdout should be a string of bytes')
        if perf_results and not isinstance(perf_results, dict):
            raise TypeError('perf_results should be a dictionary')
        if not os.path.isdir(result_dir):
            raise TypeError('%s should be a directory' % result_dir)

        with open(result_dir + '/benchmark_stdout.report', 'w') as stdout_d:
            stdout_d.write(stdout.decode('utf-8'))

        if isinstance(perf_results, dict):
            with open(result_dir + '/perf_parser_results.report', 'w') as perf_res_d:
                yaml.dump(perf_results, perf_res_d, default_flow_style=False)
        else:
            with open(result_dir + '/perf_parser_results.report', 'w') as perf_res_d:
                perf_res_d.write(perf_results)

    def _load_benchmark_model(self, benchmark_name):
        mod = importlib.import_module('models.benchmarks.' + benchmark_name)
        return mod.BenchmarkModelImplementation()

    def _load_machine_model(self, machine_type):
        mod = importlib.import_module('models.machines.' + machine_type)
        return mod.MachineModelImplementation()

    def _validate_model(self, model_name, model_type):
        filename = 'models/' + model_type + 's/' + model_name + '.py'
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

        self._make_unique_name()

        unique_root_path = os.path.join(self.args.benchmark_root,
                                        self.binary_name)
        print(unique_root_path)
        compiler_path = os.path.join(unique_root_path, 'compiler/')
        print(compiler_path)
        benchmark_path = os.path.join(unique_root_path, 'benchmark/')
        results_path = os.path.join(unique_root_path, 'results/')

        run(['mkdir', unique_root_path])
        run(['mkdir', compiler_path])
        run(['mkdir', benchmark_path])
        run(['mkdir', results_path])
        print('Made dirs')
        compiler_factory = CompilerFactory(self.args.toolchain_url,
                                           compiler_path)
        try:
            self.benchmark_model = self._validate_model(self.args.name +
                                                        '_model', 'benchmark')
        except ImportError as err:
            print(err)
            self.parser.print_help()

        print('Fetched Benchmark')

        try:
            self.machine_model = self._validate_model(self.args.machine_type +
                                                      '_model', 'machine')
        except ImportError as err:
            print(err)
            self.parser.print_help()

        print('Fetched Machine')

        try:
            self.compiler_model = compiler_factory.getCompiler()
        except ImportError as err:
            print(err)
            self.parser.print_help()

        print('Fetched Compiler')

        with cd(benchmark_path):
            for cmd in self.benchmark_model.prepare_build_benchmark(
                    self.args.benchmark_build_deps):
                run(cmd)
        print('Prepared for build')

        complete_build_flags, complete_link_flags = self._build_complete_flags()

        with cd(os.path.join(benchmark_path, self.benchmark_model.name)):
            for cmd in self.benchmark_model.build_benchmark(self.compiler_model.frontend_path,
                                                            complete_build_flags,
                                                            complete_link_flags,
                                                            self.binary_name):
                print(cmd)
                stdout, stderr = run(cmd)  # Might be useful having a build parser here
                print('stdout' + stdout)
                print('stderr' + stderr)

            print('Benchmark built !!!')

            for cmd in self.benchmark_model.prepare_run_benchmark(
                    self.args.benchmark_run_deps):
                run(cmd)

            print('Ready for run, Commander')

            run_cmd = self.benchmark_model.run_benchmark(
                self.args.benchmark_options)

            print('Benchmark has been ran, Comrade')

            perf_parser = LinuxPerf(run_cmd)
            stdout, perf_results = perf_parser.stat()

        print('The truth is out there')

        self._output_logs(stdout, perf_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run some benchmark.')
    parser.add_argument('name', metavar='benchmark_name', type=str,
                        help='The name of the benchmark to be run')
    parser.add_argument('machine_type', type=str,
                        help='The type of the machine to run the benchmark on')
    parser.add_argument('toolchain_url', type=str,
                        help='The url of the toolchain with which to compile the benchmark')
    parser.add_argument('--compiler-flags', type=str, default='',
                        help='The extra compiler flags to use with compiler')
    parser.add_argument('--link-flags', type=str, default='',
                        help='The extra link flags to use with the benchmark building')
    parser.add_argument('--benchmark-options', type=str, default='',
                        help='The benchmark options to use with the benchmark')
    parser.add_argument('--benchmark-build-deps', type=str, default='',
                        help='The benchmark specific extra dependencies for the build')
    parser.add_argument('--benchmark-run-deps', type=str, default='',
                        help='The benchmark specific extra dependencies for the run')
    parser.add_argument('--benchmark-root', type=str,
                        help='The benchmark root directory where things will be \
                        extracted and created')
    args = parser.parse_args()

    controller = BenchmarkController(parser, args)
    controller.main()
