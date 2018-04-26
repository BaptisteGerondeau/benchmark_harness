#!/usr/bin/env python3

from models.benchmarks.benchmark_model import BenchmarkModel


class BenchmarkModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""

    def __init__(self):
        super().__init__()
        self.name = 'lulesh'
        self.base_runflags = ''
        self.base_compileflags = ''
        self.base_linkflags = ''
        self.base_build_deps = ''
        self.base_run_deps = ''
        self.benchmark_url = 'https://github.com/LLNL/LULESH.git'

    def prepare_build_benchmark(self, extra_deps):
        """Prepares Environment for building and running the benchmark
        This entitles : installing dependencies, fetching benchmark code
        Can use Ansible to do this platform independantly and idempotently"""
        prepare_build_cmd = []
        return prepare_build_cmd

    def prepare_run_benchmark(self, extra_deps):
        """Prepares envrionment for running the benchmark
        This entitles : fetching the benchmark and preparing
        for running it"""
        prepare_run_cmd = []
        return prepare_run_cmd

    def build_benchmark(self, compiler, complete_compile_flags, complete_link_flags, binary_name):
        """Builds the benchmark using the base + extra flags"""
        build_cmd = []
        make_cmd = []
        make_cmd += 'make'
        make_cmd += 'CXX=' + compiler
        make_cmd += 'CXXFLAGS=' + complete_compile_flags
        make_cmd += 'LDFLAGS=' + complete_link_flags
        make_cmd += 'LULESH_EXEC="' + binary_name + '"'
        build_cmd += make_cmd
        return build_cmd

    def run_benchmark(self, extra_runflags, log_name):
        """Runs the benchmarks using the base + extra flags"""
        print(self.benchmark_url, flush=True)


# if args.name.lower() in BENCHMARK_LIST:
#    subprocess.run(['mkdir', identity])
#    with cd(identity):
#        subprocess.run(['git', 'clone', GIT_URLS[args.name.lower()], args.name.lower()], check=True)
#        with cd(args.name.lower()):
#            subprocess.run(make_cmd, check=True)
#            with open(report_name, 'w') as fd:
#                subprocess.check_call(['./' + execname, args.benchmark_options],
#                        stderr=subprocess.STDOUT, stdout=fd)
