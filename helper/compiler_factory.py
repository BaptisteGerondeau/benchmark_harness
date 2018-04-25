#!/usr/bin/env python3

import tarfile
import os
import re
import importlib
from urllib.request import urlretrieve
from pathlib import Path
from helper.cd import cd

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
        original_path = os.getcwd()
        with cd(self.toolchain_extractpath):
            with cd(extracted_tar):
                for root, dirnames,_ in os.walk('.'):
                    for dirname in dirnames:
                        if dirname == 'bin':
                            with cd(original_path):
                                return self._getCompilerFromBinaries(
                                    os.path.join(self.toolchain_extractpath,
                                                        extracted_tar, dirname))
        raise ImportError('Frontend not found...')
        return None

    def _validate_compiler_model(self, model_name):
        if os.path.isfile(model_name):
            raw = Path(model_name).read_text()
            if raw.find('class CompilerModelImplementation') == -1:
                return False
            else:
                return True
        else:
            raise ImportError('Bad Path ' + model_name)

    def _load_model(self, model_name, original_path):
        with cd(original_path):
            model_name = re.sub("[*.py]", "", model_name)
            mod = importlib.import_module('models.compilers.' + model_name)
        return mod.CompilerModelImplementation()


    def _getCompilerFromBinaries(self, bin_path):
        original_path = os.getcwd()
        list_compiler_modules = os.listdir('./models/compilers/')
        for model in list_compiler_modules:
            if model.find('_model') != -1:
                if self._validate_compiler_model(os.path.join(os.getcwd(),
                                                              'models/compilers/'
                                                              + model)):
                    loaded_model = self._load_model(model, original_path)
                    if loaded_model.check(bin_path):
                        return loaded_model
        raise ImportError('No corresponding module found for toolchain @ ' +
                          self.toolchain_url)
        return None
