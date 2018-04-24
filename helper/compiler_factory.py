#!/usr/bin/env python3

import tarfile
import os
import importlib
from urllib.request import urlretrieve
from pathlib import Path
from cd import cd

class CompilerFactory(object):
    def __init__(self, toolchain_url, toolchain_extractpath):
        self.toolchain_url = toolchain_url
        self.toolchain_extractpath = toolchain_extractpath

    def getCompiler(self):
        extracted_tar = self._downloadToolchain()
        return self._fetchCompiler(extracted_tar)

    def _downloadToolchain(self):
        with cd(self.toolchain_extractpath):
            filename, headers = urlretrieve(self.toolchain_url)
            before = os.listdir()
            tarball = tarfile.open(filename)
            tarball.extractall()
            after = os.listdir()
            filename = [x for x in after if x not in before]
            return filename[0]

    def _fetchCompiler(self, extracted_tar):
        with cd(self.toolchain_extractpath):
            with cd(extracted_tar):
                for root, dirnames,_ in os.walk('.'):
                    for dirname in dirnames:
                        if dirname == 'bin':
                            return self._getCompilerFromBinaries(os.path.join(root,
                                                                   dirname))
                        else:
                            raise FileNotFoundError('Are you sure this a correct toolchain ?')
            return None

    def _validate_compiler_model(self, model_name):
        if os.path.isfile(model_name):
            raw = Path(model_name).read_text()
            if raw.find('class CompilerModelImplementation') == -1:
                raise ImportError('Cannot find class CompilerModelImplementation in '
                                  + model_name)
            else:
                return self._load_model(model_name)
        else:
            raise ImportError('Cannot find plugin ' + model_name)

    def _load_model(self, model_name):
        mod = importlib.import_module('models.compilers' + model_name)
        return mod.CompilerModelImplementation()


    def _getCompilerFromBinaries(self, bin_path):
        list_compiler_modules = os.listdir('../models/compilers/')
        for model in list_compiler_modules:
            if self._validate_compiler_model(model):
                loaded_model = self._load_model(model)
                if loaded_model.check(bin_path):
                    return loaded_model
        return None
